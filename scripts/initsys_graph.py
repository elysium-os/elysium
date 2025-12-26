#!/usr/bin/env -S python3 -B

import os

import chariot_utils
import initsys_utils
import networkx as nx
from pyvis.network import Network
from pyvis.options import Layout

header_path = os.path.join(chariot_utils.path("source/cronus"), "include/sys/init.h")
kernel_path = os.path.join(chariot_utils.path("package/cronus"), "sys/kernel.elf")

targets = initsys_utils.init_targets(header_path, kernel_path)

graph = nx.DiGraph()
for target in targets:
    name_id = f"target_{target.name}"

    for provide in target.provides:
        provide_id = f"objective_{provide}"
        if not graph.has_node(provide_id):
            graph.add_node(provide_id, label=provide, color="#b0000c")
        graph.add_edge(provide_id, name_id, arrows={"to": False, "from": True})

    for dep in target.depends:
        dep_id = f"objective_{dep}"
        if not graph.has_node(dep_id):
            graph.add_node(dep_id, label=dep, color="#b0000c")
        graph.add_edge(name_id, dep_id)

    graph.add_node(name_id, label=target.name, color="#004ec2", shape="diamond")

net = Network(height="95vh", width="100%", directed=True)
net.from_nx(graph)
net.toggle_physics(False)

net.options.layout = Layout()
net.options.layout.hierarchical.enabled = True
net.options.layout.hierarchical.levelSeparation = 60
net.options.layout.hierarchical.treeSpacing = 100
net.options.layout.hierarchical.nodeSpacing = 100
net.options.layout.hierarchical.blockShifting = True
net.options.layout.hierarchical.edgeMinimization = True
net.options.layout.hierarchical.parentCentralization = True
net.options.layout.hierarchical.sortMethod = "directed"
net.options.layout.hierarchical.direction = "DU"
net.options.layout.hierarchical.shakeTowards = "leaves"

net.options.interaction.multiselect = True

graph_dir = "init_graph"
graph_file = "graph.html"
if not os.path.exists(graph_dir):
    os.mkdir(graph_dir)

os.chdir(graph_dir)

net.write_html(graph_file, open_browser=True)

inject = r"""
<script>
(() => {
    const KEY = "pyvis_layout_v1";

    const ready = (fn) => {
        if(typeof network !== "undefined") {
            fn();
            return;
        }

        setTimeout(() => ready(fn), 50);
    }

    ready(() => {
        const markUpEdgesInvalid = () => {
            const pos = network.getPositions();

            const updates = [];
            edges.forEach((e) => {
                const from = pos[e.from], to = pos[e.to];
                if (!from || !to) return;

                const invalid = (to.y > from.y);
                updates.push({
                    id: e.id,
                    dashes: invalid,
                    width: invalid ? 3 : 1
                });
            });
            if(updates.length > 0) edges.update(updates);
        }

        const normalizeId = (id) => {
            const n = Number(id);
            return Number.isFinite(n) && String(n) === String(id).trim() ? n : id;
        }

        try {
            const raw = localStorage.getItem(KEY);
            if(raw) {
                const saved = JSON.parse(raw);
                const existingIds = Object.keys(network.getPositions());

                const updates = [];
                for (const rawId of Object.keys(saved)) {
                    const id = normalizeId(rawId);
                    if (!existingIds.includes(id)) continue;

                    const p = saved[rawId];
                    if (!p || typeof p.x !== "number") continue;
                    updates.push({ id, x: p.x });
                }
                if(updates.length > 0) nodes.update(updates);

                markUpEdgesInvalid();
            }
        } catch(e) {
            console.warn("Failed to restore layout:", e);
        }

        network.on("dragEnd", () => {
            try {
                localStorage.setItem(KEY, JSON.stringify(network.getPositions()));
            } catch(e) {
                console.warn("Failed to save layout:", e);
            }
        });
    });
})();
</script>
"""

with open(graph_file, "r", encoding="utf-8") as f:
    html = f.read()

# Insert before </body>
html = html.replace("</body>", inject + "\n</body>")

with open(graph_file, "w", encoding="utf-8") as f:
    f.write(html)
