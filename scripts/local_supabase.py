"""Lifecycle of one worktree's local Supabase stack. Requires Linux and Python 3."""
import fcntl
import json
import os
from pathlib import Path
import re
import signal
import socket
import struct
import subprocess
import sys

PREFIX = "com.docker.network.bridge."
OPTIONS = {PREFIX + "host_binding_ipv4": "127.0.0.1", PREFIX + "gateway_mode_ipv4": "nat",
           PREFIX + "gateway_mode_ipv6": "nat", PREFIX + "enable_ip_masquerade": "true",
           PREFIX + "enable_icc": "true"}
CLI_LABEL = "com.supabase.cli.project"
SLOT = "io.growthly.slot"
SERVICES = "db kong auth inbucket realtime rest storage imgproxy pg_meta studio edge_runtime analytics vector pooler".split()
# Multi-architecture BusyBox 1.37. The native firewall probe only sleeps, with no published ports.
PROBE_IMAGE = "busybox@sha256:a7dbc319b1438115a207e11930dc4bb3e643dcb3ec0bdd694bb36cd8fad289ec"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def output(*args):
    return subprocess.check_output(args, text=True).strip()


def docker(*args):
    return output("docker", *args)


def inspect(kind, ids):
    if not ids:
        return []
    return json.loads(docker(kind, "inspect", *ids))


def slirp_boundary():
    """Recognize a local rootless daemon behind RootlessKit user-mode NAT."""
    host = os.environ.get("DOCKER_HOST") if not os.environ.get("DOCKER_CONTEXT") else None
    host = host or docker("context", "inspect", "--format", "{{.Endpoints.docker.Host}}")
    require(host.startswith("unix://"), "Run on the local Docker host.")
    with socket.socket(socket.AF_UNIX) as sock:
        sock.connect(host[7:])
        pid, _, _ = struct.unpack("3i", sock.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
    if "name=rootless" not in docker("info", "--format", "{{json .SecurityOptions}}"):
        return False
    proc = Path(f"/proc/{pid}")
    require((proc / "comm").read_text().strip() == "dockerd", "Cannot identify the rootless daemon.")
    while pid > 1:
        proc = Path(f"/proc/{pid}")
        args = (proc / "cmdline").read_bytes().split(b"\0")
        if (proc / "comm").read_text().strip() == "rootlesskit":
            require(b"--net=slirp4netns" in args and b"--port-driver=builtin" in args,
                    "Unsupported RootlessKit routing or port driver.")
            return True
        pid = int(re.search(r"^PPid:\s*(\d+)", (proc / "status").read_text(), re.M)[1])
    raise RuntimeError("Cannot verify a RootlessKit/slirp4netns boundary.")


def check_raw_rules(network_id, addresses):
    # Read the actual packet filter. A loopback HostIp alone says nothing about direct routing.
    command = ["iptables", "-t", "raw", "-S", "PREROUTING"]
    rules = output(*(command if os.geteuid() == 0 else ["sudo", "-n", *command])).splitlines()
    for address in addresses:
        expected = f"-A PREROUTING -d {address}/32 ! -i br-{network_id[:12]} -j DROP"
        for rule in rules:
            if rule == expected:
                break
            # Refuse an earlier exemption or custom chain whose effect is unknown.
            require(not rule.startswith("-A ") or rule.endswith(" -j DROP"),
                    "Unverified earlier raw PREROUTING rule: " + rule)
        else:
            raise RuntimeError("Missing Docker direct-routing DROP rule for " + address)


class Stack:
    def __init__(self, root, worktree_hash, slot):
        self.root = root
        self.project = "growthly-" + worktree_hash[:16]
        self.name = self.project + "-loopback"
        self.base = 54000 + 10 * slot
        self.labels = {"io.growthly.project": self.project, "io.growthly.worktree": worktree_hash,
                       SLOT: str(slot)}
        self.names = {f"supabase_{service}_{self.project}": service for service in SERVICES}

    def network(self):
        ids = docker("network", "ls", "--no-trunc", "-q", "--filter", f"name=^{self.name}$").split()
        if not ids:
            return None
        require(len(ids) == 1, "Ambiguous network name.")
        net = inspect("network", ids)[0]
        require(net["Name"] == self.name and net["Labels"] == self.labels,
                f"Foreign or unlabeled network {self.name}; inspect manually.")
        require(net["Driver"] == "bridge" and net["Scope"] == "local" and
                not any(net[k] for k in ("Internal", "Ingress", "Attachable", "ConfigOnly", "EnableIPv6"))
                and net.get("EnableIPv4", True) and not net.get("ConfigFrom", {}).get("Network")
                and net["IPAM"]["Driver"] == "default" and not net["IPAM"].get("Options")
                and net["Options"] == OPTIONS, "Unexpected Docker network policy.")
        return net

    def containers(self):
        ids = docker("ps", "-aq", "--no-trunc", "--filter", f"label={CLI_LABEL}={self.project}").split()
        return inspect("container", ids)

    def owned_member(self, net, c):
        links = c["NetworkSettings"]["Networks"] or {}
        return (net and c["Name"].lstrip("/") in self.names and
                c["Config"]["Labels"].get(CLI_LABEL) == self.project and
                c["Config"]["Labels"].get("com.docker.compose.project") == self.project and
                c["HostConfig"]["NetworkMode"] == self.name and
                set(links) <= {self.name} and
                all(link["NetworkID"] in ("", net["Id"]) for link in links.values()))

    def members(self, net):
        members = self.containers()
        endpoints = set((net or {}).get("Containers") or {})
        running = set()
        for c in members:
            name = c["Name"].lstrip("/")
            links = c["NetworkSettings"]["Networks"]
            require(self.owned_member(net, c), "Unexpected project container: " + name)
            if c["State"]["Running"]:
                require(links.get(self.name, {}).get("NetworkID") == net["Id"],
                        "Missing or unexpected network attachment: " + name)
                running.add(c["Id"])
        require(running == endpoints, "Unexpected or missing Docker network endpoint.")
        return members

    def verify(self, net, members, rootless):
        ports = {"db": ("5432/tcp", 2), "kong": ("8000/tcp", 1), "studio": ("3000/tcp", 3),
                 "inbucket": ("8025/tcp", 4), "analytics": ("4000/tcp", 5), "pooler": ("6543/tcp", 7)}
        found = set()
        addresses = []
        for c in members:
            service = self.names[c["Name"].lstrip("/")]
            require(c["State"]["Running"], "Stopped project container: " + service)
            addresses.append(c["NetworkSettings"]["Networks"][self.name]["IPAddress"])
            for private, bindings in (c["NetworkSettings"]["Ports"] or {}).items():
                if bindings:
                    expected, offset = ports.get(service, (None, 0))
                    require(private == expected and bindings == [
                        {"HostIp": "127.0.0.1", "HostPort": str(self.base + offset)}],
                        "Unexpected published port on " + service)
                    found.add(service)
                    print(f"{service}  127.0.0.1:{self.base + offset}", flush=True)
        require({"db", "kong"} <= found, "Missing API or database mapping.")
        if not rootless:
            check_raw_rules(net["Id"], addresses)

    def cli(self, *args):
        keys = ["DB_SHADOW_PORT", "API_PORT", "DB_PORT", "STUDIO_PORT", "INBUCKET_PORT",
                "ANALYTICS_PORT", "EDGE_RUNTIME_INSPECTOR_PORT", "DB_POOLER_PORT"]
        env = dict(os.environ, SUPABASE_PROJECT_ID=self.project)
        env.update({"SUPABASE_" + key: str(self.base + i) for i, key in enumerate(keys)})
        subprocess.run(["supabase", "--workdir", self.root, "--network-id", self.name, *args],
                       env=env, check=True)

    def volumes(self):
        expected = {f"supabase_{role}_{self.project}" for role in ("db", "storage")}
        existing = expected.intersection(docker("volume", "ls", "-q").split())
        for vol in inspect("volume", sorted(existing)):
            require((vol["Labels"] or {}).get(CLI_LABEL) == self.project, "Foreign volume: " + vol["Name"])
        return existing

    def preflight(self):
        # CLI 2.75.0 prunes by its project label internally on startup failure.
        require(not docker("network", "ls", "-q", "--filter", f"label={CLI_LABEL}={self.project}"),
                "An existing network would be subject to Supabase CLI pruning.")
        require(not self.names.keys() & set(docker("ps", "-a", "--format", "{{.Names}}").split()),
                "A service container name is already in use.")
        claims = docker("network", "ls", "--filter", f"label={SLOT}={self.labels[SLOT]}",
                        "--format", "{{.Name}}").split()
        require(all(n == self.name for n in claims), "Worktree slot already reserved.")

    def probe(self, net):
        # No service is listening during this check. Only remove the ID returned by docker run.
        cid = docker("run", "-d", "--rm", "--network", net["Id"], "--cap-drop=ALL",
                     "--read-only", PROBE_IMAGE, "sleep", "60")
        try:
            link = inspect("container", [cid])[0]["NetworkSettings"]["Networks"][self.name]
            check_raw_rules(net["Id"], [link["IPAddress"]])
        finally:
            docker("rm", "-f", cid)

    def cleanup(self, net_id, remove_net, old_volumes=None):
        net = self.network()
        require(net and net["Id"] == net_id, "Network identity changed during cleanup.")
        if old_volumes is None:
            members = self.members(net)
        else:
            # Start was entered with zero project containers. Clean up provable additions
            # even if a foreign endpoint appeared; Docker refuses removal of an occupied bridge.
            members = [c for c in self.containers() if self.owned_member(net, c)]
        for c in members:
            if c["State"]["Running"]:
                docker("stop", c["Id"])
            docker("rm", "-v", c["Id"])
        if old_volumes is not None:
            for volume in self.volumes() - old_volumes:
                docker("volume", "rm", volume)
        if remove_net:
            self.remove_empty_network(net_id)

    def remove_empty_network(self, net_id):
        net = self.network()
        require(net and net["Id"] == net_id and not net["Containers"], "Network occupied or replaced.")
        docker("network", "rm", net_id)

    def run(self, command):
        net = self.network()
        members = self.members(net)
        if command == "stop":
            if net:
                self.cleanup(net["Id"], True)
            return
        require(int(docker("version", "--format", "{{.Server.Version}}").split(".")[0]) >= 28,
                "Docker Engine 28 or newer required.")
        rootless = slirp_boundary()
        if command != "start" or members:
            require(net, "No worktree network.")
            self.verify(net, members, rootless)
            if command == "status":
                self.cli("status")
            elif command == "reset":
                self.cli("db", "reset", "--local")
            return

        self.preflight()
        old_volumes = self.volumes()
        created = net is None
        if created:
            args = []
            for flag, values in [("--label", self.labels), ("--opt", OPTIONS)]:
                for key, value in values.items():
                    args += [flag, f"{key}={value}"]
            net_id = docker("network", "create", "--driver", "bridge", *args, self.name)
        else:
            net_id = net["Id"]
        cli_started = False
        try:
            net = self.network()
            require(net and net["Id"] == net_id, "Created network identity mismatch.")
            self.preflight()
            if not rootless:
                self.probe(net)
            cli_started = True
            self.cli("start")
            net = self.network()
            require(net and net["Id"] == net_id, "Network replaced during start.")
            self.verify(net, self.members(net), rootless)
        except BaseException:
            if cli_started:
                self.cleanup(net_id, created, old_volumes)
            elif created:
                self.remove_empty_network(net_id)
            raise


def main():
    require(len(sys.argv) == 2 and sys.argv[1] in {"start", "stop", "status", "ports", "reset"},
            "Usage: local-supabase.sh {start|stop|status|ports|reset}")
    root = output("git", "rev-parse", "--show-toplevel")
    slot = (Path(root) / ".growthly-slot").read_text().strip()
    require(re.fullmatch(r"[1-9][0-9]?", slot), "Choose a worktree slot from 1 to 99.")
    worktree_hash = subprocess.check_output(["git", "hash-object", "--stdin"], input=root.encode()).decode().strip()
    lock = Path(output("git", "rev-parse", "--absolute-git-dir")) / "growthly-lifecycle.lock"
    with lock.open("a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        Stack(root, worktree_hash, int(slot)).run(sys.argv[1])


if __name__ == "__main__":
    def interrupted(signum, frame):
        raise KeyboardInterrupt("Supabase operation interrupted")
    signal.signal(signal.SIGTERM, interrupted)
    try:
        main()
    except (RuntimeError, OSError, subprocess.CalledProcessError, KeyboardInterrupt) as error:
        sys.exit(str(error) or "Interrupted")
