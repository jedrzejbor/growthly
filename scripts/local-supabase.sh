#!/usr/bin/env bash
set -euo pipefail

root=$(git rev-parse --show-toplevel)
cd "$root"
if [[ ! -f .growthly-slot ]]; then
  echo "Assign this worktree a port slot in .growthly-slot (1 through 99). See docs/DATABASE.md." >&2
  exit 2
fi
slot=$(cat .growthly-slot)
[[ $slot =~ ^[1-9][0-9]?$ ]] || { echo "Invalid worktree slot: $slot" >&2; exit 2; }
base=$((54000 + 10 * slot))
# A copied slot file can cause a port collision, but cannot select another worktree's project.
path_hash=$(printf '%s' "$root" | git hash-object --stdin)
export SUPABASE_PROJECT_ID="growthly-${path_hash:0:16}"
export SUPABASE_DB_SHADOW_PORT=$base SUPABASE_API_PORT=$((base+1)) SUPABASE_DB_PORT=$((base+2))
export SUPABASE_STUDIO_PORT=$((base+3)) SUPABASE_INBUCKET_PORT=$((base+4))
export SUPABASE_ANALYTICS_PORT=$((base+5)) SUPABASE_EDGE_RUNTIME_INSPECTOR_PORT=$((base+6))
export SUPABASE_DB_POOLER_PORT=$((base+7))
network="$SUPABASE_PROJECT_ID-loopback"
cli=(supabase --workdir "$root" --network-id "$network")
binding=com.docker.network.bridge.host_binding_ipv4

check_ports() {
  local ids id mappings address port count=0
  ids=$(docker ps -q --filter "label=com.supabase.cli.project=$SUPABASE_PROJECT_ID")
  [[ -n $ids ]] || { echo "No running containers for $SUPABASE_PROJECT_ID" >&2; return 1; }
  for id in $ids; do
    [[ $(docker inspect -f '{{.HostConfig.NetworkMode}}' "$id") == "$network" ]] || return 1
    mappings=$(docker inspect -f '{{range .NetworkSettings.Ports}}{{range .}}{{println .HostIp .HostPort}}{{end}}{{end}}' "$id") || return 1
    while read -r address port; do
      [[ -n $address ]] || continue
      echo "$id  $address:$port"
      [[ $address == 127.0.0.1 && $port -ge $base && $port -lt $((base+10)) ]] || return 1
      count=$((count+1))
    done <<< "$mappings"
  done
  [[ $count -ge 2 ]] || return 1
  [[ $(docker port "supabase_db_$SUPABASE_PROJECT_ID" 5432/tcp) == "127.0.0.1:$SUPABASE_DB_PORT" ]]
}

case "${1:-}" in
  start)
    engine=$(docker version --format '{{.Server.Version}}')
    [[ ${engine%%.*} -ge 28 ]] || { echo "Loopback publishing requires Docker Engine 28 or newer." >&2; exit 1; }
    if ! docker network inspect "$network" > /dev/null 2>&1; then
      docker network create --driver bridge --opt "$binding=127.0.0.1" "$network"
    fi
    actual=$(docker network inspect -f '{{.Driver}} {{index .Options "com.docker.network.bridge.host_binding_ipv4"}}' "$network")
    [[ $actual == "bridge 127.0.0.1" ]] || { echo "Unsafe network settings for $network" >&2; exit 1; }
    "${cli[@]}" start
    if ! check_ports; then
      echo "Unexpected network or port mappings. Stopping this project." >&2
      "${cli[@]}" stop
      exit 1
    fi ;;
  ports) check_ports ;;
  status) check_ports >&2 && "${cli[@]}" status ;;
  stop) "${cli[@]}" stop ;;
  reset) check_ports && "${cli[@]}" db reset --local ;;
  *) echo "Usage: $0 {start|status|ports|stop|reset}" >&2; exit 2 ;;
esac
