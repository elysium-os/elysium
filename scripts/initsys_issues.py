#!/usr/bin/env -S python3 -B

from __future__ import annotations

import os
from collections import defaultdict, deque
from typing import Dict, List, Optional, Set, Tuple

import chariot_utils
from initsys_utils import Target, init_targets
from termcolor import colored


def build_provider_index(targets: List[Target]) -> Dict[str, List[int]]:
    providers: Dict[str, List[int]] = defaultdict(list)
    for i, t in enumerate(targets):
        for pid in t.provides:
            providers[pid].append(i)
    return providers


def build_edges_all_providers(
    targets: List[Target],
) -> Tuple[Dict[int, Set[int]], Dict[Tuple[int, int], Set[str]], List[Tuple[str, str]]]:
    prov = build_provider_index(targets)
    adjacency: Dict[int, Set[int]] = {i: set() for i in range(len(targets))}
    edge_labels: Dict[Tuple[int, int], Set[str]] = defaultdict(set)
    missing: List[Tuple[str, str]] = []

    for i, t in enumerate(targets):
        for dep_id in t.depends:
            ps = prov.get(dep_id)
            if not ps:
                missing.append((t.name, dep_id))
                continue
            for p in ps:
                adjacency[i].add(p)
                edge_labels[(i, p)].add(dep_id)

    return adjacency, edge_labels, missing


def tarjan_scc(adjacency: Dict[int, Set[int]], n: int) -> List[List[int]]:
    index = 0
    stack: List[int] = []
    onstack = [False] * n
    idx = [-1] * n
    low = [0] * n
    sccs: List[List[int]] = []

    def dfs(v: int) -> None:
        nonlocal index
        idx[v] = index
        low[v] = index
        index += 1
        stack.append(v)
        onstack[v] = True

        for w in adjacency[v]:
            if idx[w] == -1:
                dfs(w)
                low[v] = min(low[v], low[w])
            elif onstack[w]:
                low[v] = min(low[v], idx[w])

        if low[v] == idx[v]:
            comp: List[int] = []
            while True:
                w = stack.pop()
                onstack[w] = False
                comp.append(w)
                if w == v:
                    break
            sccs.append(comp)

    for v in range(n):
        if idx[v] == -1:
            dfs(v)

    return sccs


def shortest_cycle_in_scc(adjacency: Dict[int, Set[int]], nodes: Set[int]) -> Optional[List[int]]:
    best: Optional[List[int]] = None

    for start in nodes:
        q = deque([start])
        parent: Dict[int, int] = {}
        visited: Set[int] = {start}

        while q:
            u = q.popleft()
            for v in adjacency[u]:
                if v not in nodes:
                    continue
                if v == start:
                    path = [u]
                    while path[-1] != start:
                        path.append(parent[path[-1]])
                    path.reverse()
                    cycle = path + [start]
                    if best is None or len(cycle) < len(best):
                        best = cycle
                    q.clear()
                    break
                if v not in visited:
                    visited.add(v)
                    parent[v] = u
                    q.append(v)

    return best


def pretty_print_cycle(
    cycle: List[int],
    targets: List[Target],
    providers: Dict[str, List[int]],
    edge_labels: Dict[Tuple[int, int], Set[str]],
) -> None:
    print("Shortest actionable cycle:")
    for a, b in zip(cycle, cycle[1:]):
        dep_ids = sorted(edge_labels.get((a, b), set()))
        if not dep_ids:
            print(f"  {targets[a].name} -> {targets[b].name}")
            continue

        dep_parts = []
        for dep_id in dep_ids:
            provs = providers.get(dep_id, [])
            single = len(provs) == 1
            mark = " (single provider)" if single else ""
            dep_parts.append(f"{dep_id}{mark}")
        deps_str = ", ".join(dep_parts)

        print(f"    {colored(targets[a].name, 'blue')} -> {colored(deps_str, 'yellow')} -> {colored(targets[b].name, 'blue')}")

    print()


def analyze(targets: List[Target]) -> None:
    adjacency, edge_labels, missing = build_edges_all_providers(targets)
    providers = build_provider_index(targets)

    if missing:
        print("Missing dependencies:")
        for t, dep in missing:
            print(f"  - {colored(t, 'blue')} missing {colored(dep, 'yellow')}")
        print()

    sccs = tarjan_scc(adjacency, len(targets))
    cyclic_sccs = []
    for comp in sccs:
        if len(comp) > 1:
            cyclic_sccs.append(comp)
        elif comp[0] in adjacency[comp[0]]:
            cyclic_sccs.append(comp)

    if not cyclic_sccs:
        print("No cycles detected.")
        return

    # Print each SCC, but also provide shortest cycle with annotated edges
    for comp in cyclic_sccs:
        nodes = set(comp)
        names = sorted(targets[i].name for i in nodes)
        print(f"Cycle group size={len(nodes)}: {colored(', '.join(names), 'blue')}")

        cyc = shortest_cycle_in_scc(adjacency, nodes)
        if cyc is None:
            print("  (Could not extract a concrete cycle path, unexpected.)\n")
            continue
        pretty_print_cycle(cyc, targets, providers, edge_labels)


header_path = os.path.join(chariot_utils.path("source/cronus"), "include/sys/init.h")
kernel_path = os.path.join(chariot_utils.path("package/cronus"), "sys/kernel.elf")

targets = init_targets(header_path, kernel_path)

targets.sort(key=lambda t: t.name)

print("All targets:")
for target in targets:
    print(f"{colored(target.name, 'blue')} | {colored(', '.join(target.provides), 'green')} | {colored(', '.join(target.depends), 'red')}")

print()

analyze(targets)
