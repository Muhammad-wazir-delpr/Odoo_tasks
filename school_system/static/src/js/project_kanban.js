/** @odoo-module **/

import { KanbanRecord } from "@web/views/kanban/kanban_record";
import { patch } from "@web/core/utils/patch";
import { onMounted } from "@odoo/owl";

patch(KanbanRecord.prototype, {

    setup() {
        super.setup();

        onMounted(() => {
            if (!this.el) return;

            // Find the "Open in New Tab" anchor inside this kanban card
            this.el.querySelectorAll(".o_open_new_tab").forEach((link) => {
                link.addEventListener("click", (ev) => {
                    // Prevent href="#" from scrolling to top
                    ev.preventDefault();
                    // Prevent kanban card from also opening the record
                    ev.stopPropagation();

                    const id = this.props.record.resId;
                    const url = `/web#id=${id}&model=project.project&view_type=form`;
                    window.open(url, "_blank");
                });
            });
        });
    },

});