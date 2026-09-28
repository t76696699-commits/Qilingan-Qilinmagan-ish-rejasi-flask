document.addEventListener('DOMContentLoaded', () => {
    const sirtqiList = document.querySelector('.sirtqi_list');
    const ichidanOchiladigan = document.querySelector('.ichidan_ochiladigan');
    const subtaskHeaderTitle = document.getElementById('subtask-header-title');

    const addMainForm = document.getElementById('add-main-form');
    const addSubForm = document.getElementById('add-sub-form');
    const mainTaskSelect = document.getElementById('main_task_select');

    let activeMainId = null;

    // Sirtqi vazifa bosilganda ochish yoki qayta bosilganda yopish (toggle)
    sirtqiList.addEventListener('click', (e) => {
        const item = e.target.closest('.main-item');
        if (!item) return;

        const clickedId = item.dataset.id;

        // Agar allaqachon faol bo'lgan sirtqiga qayta bosilsa (yopish logic)
        if (activeMainId === clickedId) {
            item.classList.remove('active-main');
            activeMainId = null;
            resetSubtasksView();
            return;
        }

        // Barcha sirtqilardan 'active-main' ni olib tashlab, yangisiga qo'shish
        document.querySelectorAll('.main-item').forEach(el => el.classList.remove('active-main'));
        item.classList.add('active-main');

        activeMainId = clickedId;
        loadSubtasks(activeMainId);
    });

    // Ichki vazifalar oynasini boshlang'ich holatga qaytarish funksiyasi
    function resetSubtasksView() {
        subtaskHeaderTitle.textContent = 'Ichidagi narsalar';
        ichidanOchiladigan.innerHTML = '<p class="placeholder-text">Sirtqi vazifalardan birini bosing...</p>';
    }

    async function loadSubtasks(mainId) {
        const res = await fetch(`/api/main-task/${mainId}/subtasks`);
        if (!res.ok) return;

        const data = await res.json();
        subtaskHeaderTitle.textContent = `${data.main_title} — Ichidagi narsalar`;
        ichidanOchiladigan.innerHTML = '';

        if (data.subtasks.length === 0) {
            ichidanOchiladigan.innerHTML = '<p class="placeholder-text">Hali ichki vazifalar kiritilmagan</p>';
            return;
        }

        data.subtasks.forEach(sub => {
            const subRow = createSubtaskElement(sub);
            ichidanOchiladigan.appendChild(subRow);
        });
    }

    function createSubtaskElement(sub) {
        const row = document.createElement('div');
        row.className = 'sub-item';
        row.dataset.id = sub.id;

        const leftDiv = document.createElement('div');
        leftDiv.className = 'todo-left';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'todo-checkbox';
        checkbox.checked = sub.is_done;

        const h2 = document.createElement('h2');
        h2.textContent = sub.title;
        if (sub.is_done) h2.classList.add('completed-text');

        checkbox.addEventListener('change', async () => {
            const res = await fetch(`/api/subtask/toggle/${sub.id}`, { method: 'POST' });
            if (res.ok) {
                const updated = await res.json();
                h2.classList.toggle('completed-text', updated.is_done);
            }
        });

        leftDiv.appendChild(checkbox);
        leftDiv.appendChild(h2);
        row.appendChild(leftDiv);

        return row;
    }

    // 1. Yangi Sirtqi vazifa qo'shish
    addMainForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const input = addMainForm.querySelector('input[name="main_title"]');
        const title = input.value.trim();
        if (!title) return;

        const res = await fetch('/api/main-task/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title })
        });

        if (res.ok) {
            const newMain = await res.json();

            const div = document.createElement('div');
            div.className = 'main-item';
            div.dataset.id = newMain.id;
            div.innerHTML = `<h2>${newMain.title}</h2><i class="fa-solid fa-chevron-right" style="color: #00ff66;"></i>`;
            sirtqiList.appendChild(div);

            const option = document.createElement('option');
            option.value = newMain.id;
            option.textContent = newMain.title;
            mainTaskSelect.appendChild(option);

            input.value = '';
        }
    });

    // 2. Yangi Ichki vazifa qo'shish
    addSubForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const mainId = mainTaskSelect.value;
        const input = addSubForm.querySelector('input[name="sub_title"]');
        const title = input.value.trim();

        if (!mainId || !title) return;

        const res = await fetch('/api/subtask/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ main_task_id: mainId, title })
        });

        if (res.ok) {
            const newSub = await res.json();

            if (activeMainId == mainId) {
                const placeholder = ichidanOchiladigan.querySelector('.placeholder-text');
                if (placeholder) placeholder.remove();

                const subRow = createSubtaskElement(newSub);
                ichidanOchiladigan.appendChild(subRow);
            }
            input.value = '';
        }
    });
});