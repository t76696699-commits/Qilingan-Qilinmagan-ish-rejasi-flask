document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('header form');
    const input = document.querySelector('input[name="title"]');
    const qilingan = document.querySelector('.qilingan');
    const qilinmagan = document.querySelector('.qilinmagan');

    // Bitta todo qatori uchun DOM elementini yasaydi
    function createRow(item, isDone) {
        const row = document.createElement('div');
        row.className = 'h2';
        row.dataset.id = item.id;

        const h2 = document.createElement('h2');
        h2.textContent = item.title;
        row.appendChild(h2);

        const actions = document.createElement('div');
        actions.className = 'actions';

        const toggleLink = document.createElement('a');
        toggleLink.href = '#';
        toggleLink.title = isDone ? "Qilinmaganga o'tkazish" : 'Bajarildi';
        toggleLink.innerHTML = isDone
            ? '<i class="fa-solid fa-rotate-left" style="color:#00ff66;"></i>'
            : '<i class="fa-solid fa-square-check" style="color:#00ff66;"></i>';

        actions.appendChild(toggleLink);
        row.appendChild(actions);

        bindRow(row, isDone);
        return row;
    }

    // Mavjud (server tomonidan chizilgan yoki yangi yaratilgan) qatorga hodisani ulaydi
    function bindRow(row, isDone) {
        const id = row.dataset.id;
        const toggleLink = row.querySelector('a');
        if (!toggleLink) return;
        toggleLink.addEventListener('click', (e) => {
            e.preventDefault();
            toggleTodo(id, row, isDone);
        });
    }

    async function toggleTodo(id, row, wasDone) {
        const res = await fetch(`/api/toggle/${id}`, { method: 'POST' });
        if (!res.ok) return;
        const data = await res.json();
        row.remove();
        const target = wasDone ? qilinmagan : qilingan;
        target.appendChild(createRow(data, !wasDone));
    }

    // Sahifa server tomonidan chizib berilgan mavjud qatorlarni yo'qotmasdan,
    // faqat ularga hodisalarni ulaymiz (arrayga qayta yozib chiqmaymiz!)
    qilingan.querySelectorAll(':scope > .h2').forEach((row) => bindRow(row, true));
    qilinmagan.querySelectorAll(':scope > .h2').forEach((row) => bindRow(row, false));

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const title = input.value.trim();
            if (!title) return;

            const res = await fetch('/api/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title })
            });
            if (!res.ok) return;

            const item = await res.json();
            qilinmagan.appendChild(createRow(item, false));
            input.value = '';
        });
    }
});