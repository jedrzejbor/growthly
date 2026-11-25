import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import local_supabase as launcher


class Docker:
    """Small in-memory model of the inspect/list/remove operations used by the launcher."""
    def __init__(self, stack):
        self.stack = stack
        self.net = None
        self.containers = {}
        self.volumes = {}
        self.other_slots = []
        self.mutations = []

    def bridge(self):
        return {"Name": self.stack.name, "Id": "network-id", "Labels": self.stack.labels.copy(),
                "Scope": "local", "Driver": "bridge", "Internal": False, "Ingress": False,
                "Attachable": False, "ConfigOnly": False, "EnableIPv6": False,
                "IPAM": {"Driver": "default"}, "Options": launcher.OPTIONS.copy(), "Containers": {}}

    def add(self, role, private, offset):
        name = f"supabase_{role}_{self.stack.project}"
        labels = {key: self.stack.project for key in (launcher.CLI_LABEL, "com.docker.compose.project")}
        self.containers[role] = {
            "Id": role, "Name": "/" + name, "Config": {"Labels": labels},
            "HostConfig": {"NetworkMode": self.stack.name}, "State": {"Running": True},
            "NetworkSettings": {"Networks": {self.stack.name: {"NetworkID": self.net["Id"],
                                                               "IPAddress": "172.18.0.2"}},
                                "Ports": {private: [{"HostIp": "127.0.0.1",
                                                     "HostPort": str(self.stack.base + offset)}]}}}
        self.net["Containers"][role] = {"Name": name}

    def start(self, *args):
        self.add("db", "5432/tcp", 2)
        self.add("kong", "8000/tcp", 1)
        for role in ["db", "storage"]:
            name = f"supabase_{role}_{self.stack.project}"
            self.volumes[name] = {"Name": name, "Labels": {launcher.CLI_LABEL: self.stack.project}}

    def __call__(self, *args):
        first, *rest = args
        if first == "version":
            return "29.0.0"
        if first == "ps":
            if "-aq" in rest:
                return "\n".join(i for i, c in self.containers.items()
                                 if c["Config"]["Labels"].get(launcher.CLI_LABEL) == self.stack.project)
            return "\n".join(c["Name"].lstrip("/") for c in self.containers.values())
        if rest[0] == "inspect":
            objs = {"volume": self.volumes, "container": self.containers,
                    "network": {"network-id": self.net}}[first]
            return json.dumps([objs[i] for i in rest[1:]])
        if first == "volume" and rest[0] == "ls":
            return "\n".join(self.volumes)
        if first == "network" and rest[0] == "ls":
            if "--format" in rest:
                return "\n".join(self.other_slots + ([self.net["Name"]] if self.net else []))
            if rest[-1].startswith("name="):
                return "network-id" if self.net else ""
            return ""
        self.mutations.append(args)
        if (first, rest[0]) == ("network", "create"):
            self.net = self.bridge()
            return self.net["Id"]
        if (first, rest[0]) == ("network", "rm"):
            assert not self.net["Containers"] and rest[-1] == self.net["Id"]
            self.net = None
        elif first == "stop":
            self.containers[rest[-1]]["State"]["Running"] = False
        elif first == "rm":
            del self.containers[rest[-1]]
            del self.net["Containers"][rest[-1]]
        elif (first, rest[0]) == ("volume", "rm"):
            del self.volumes[rest[-1]]
        else:
            raise AssertionError(args)
        return ""


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.stack = launcher.Stack("/checkout", "a" * 40, 11)
        self.engine = Docker(self.stack)
        for substitute in [patch.object(launcher, "docker", side_effect=self.engine),
                           patch.object(launcher, "slirp_boundary", return_value=True),
                           patch.object(self.stack, "cli", side_effect=self.engine.start)]:
            substitute.start()
            self.addCleanup(substitute.stop)

    def reject_existing(self, change):
        self.engine.net = self.engine.bridge()
        change(self.engine.net)
        for command in ["start", "stop"]:
            with self.assertRaises(RuntimeError):
                self.stack.run(command)
        self.assertEqual(self.engine.mutations, [])

    def test_foreign_network(self):
        self.reject_existing(lambda n: n["Labels"].update({"io.growthly.worktree": "foreign"}))

    def test_unlabeled_network(self):
        self.reject_existing(lambda n: n.update(Labels={}))

    def test_unsafe_routing(self):
        for option, value in [("gateway_mode_ipv4", "routed"), ("gateway_mode_ipv4", "nat-unprotected"),
                              ("trusted_host_interfaces", "eth0"), ("host_binding_ipv4", "0.0.0.0")]:
            with self.subTest(option=option, value=value):
                self.reject_existing(lambda n: n["Options"].update({launcher.PREFIX + option: value}))

    def test_unexpected_endpoint(self):
        self.reject_existing(lambda n: n["Containers"].update(intruder={"Name": "foreign"}))

    def test_start_stop_and_repeated_stop_preserve_data(self):
        self.stack.run("start")
        self.stack.run("start")
        self.stack.run("stop")
        mutations = self.engine.mutations.copy()
        self.stack.run("stop")
        self.assertIsNone(self.engine.net)
        self.assertFalse(self.engine.containers)
        self.assertEqual(len(self.engine.volumes), 2)
        self.assertEqual(mutations, self.engine.mutations)

    def test_failed_start_preserves_preexisting_volume(self):
        old = "supabase_db_" + self.stack.project
        self.engine.volumes[old] = {"Name": old, "Labels": {launcher.CLI_LABEL: self.stack.project}}
        def fail(*args):
            self.engine.start()
            raise KeyboardInterrupt()
        self.stack.cli.side_effect = fail
        with self.assertRaises(KeyboardInterrupt):
            self.stack.run("start")
        self.assertFalse(self.engine.containers)
        self.assertIsNone(self.engine.net)
        self.assertEqual(list(self.engine.volumes), [old])

    def test_failed_start_preserves_reused_network(self):
        self.engine.net = self.engine.bridge()
        self.stack.cli.side_effect = RuntimeError("startup failed")
        with self.assertRaisesRegex(RuntimeError, "startup failed"):
            self.stack.run("start")
        self.assertEqual(self.engine.net["Id"], "network-id")
        self.assertFalse(self.engine.mutations)

    def test_duplicate_slot(self):
        self.engine.other_slots.append("another-worktree-loopback")
        with self.assertRaisesRegex(RuntimeError, "slot already reserved"):
            self.stack.run("start")
        self.assertFalse(self.engine.mutations)

    def test_foreign_volume(self):
        self.engine.volumes["supabase_db_" + self.stack.project] = {"Labels": {}, "Name": "foreign"}
        with self.assertRaisesRegex(RuntimeError, "Foreign volume"):
            self.stack.run("start")
        self.assertFalse(self.engine.mutations)

    def test_external_attachment(self):
        self.stack.run("start")
        self.engine.containers["db"]["NetworkSettings"]["Networks"]["other"] = {"NetworkID": "other"}
        before = self.engine.mutations.copy()
        with self.assertRaises(RuntimeError):
            self.stack.run("stop")
        self.assertEqual(self.engine.mutations, before)

    def test_failed_start_with_unrelated_endpoint(self):
        def contaminate(*args):
            self.engine.start()
            self.engine.net["Containers"]["foreign"] = {"Name": "other-project"}
        self.stack.cli.side_effect = contaminate
        with self.assertRaisesRegex(RuntimeError, "occupied"):
            self.stack.run("start")
        self.assertEqual(set(self.engine.net["Containers"]), {"foreign"})
        self.assertFalse(self.engine.containers)

    def test_incorrect_actual_port_rolls_back(self):
        def wrong_port(*args):
            self.engine.start()
            self.engine.containers["db"]["NetworkSettings"]["Ports"]["5432/tcp"][0]["HostIp"] = "::"
        self.stack.cli.side_effect = wrong_port
        with self.assertRaisesRegex(RuntimeError, "published port"):
            self.stack.run("start")
        self.assertIsNone(self.engine.net)

    def test_missing_daemon_direct_routing_protection(self):
        with patch.object(launcher, "output", return_value="-P PREROUTING ACCEPT"):
            with self.assertRaisesRegex(RuntimeError, "Missing Docker direct-routing"):
                launcher.check_raw_rules("a"*64, ["172.17.0.3"])

    def test_earlier_firewall_exemption(self):
        rules = "-A PREROUTING -j ACCEPT\n-A PREROUTING -d 172.17.0.3/32 ! -i br-aaaaaaaaaaaa -j DROP"
        with patch.object(launcher, "output", return_value=rules):
            with self.assertRaisesRegex(RuntimeError, "earlier raw"):
                launcher.check_raw_rules("a"*64, ["172.17.0.3"])
