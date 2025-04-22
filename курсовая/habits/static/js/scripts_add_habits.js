document.addEventListener('DOMContentLoaded', function() {
    // Инициализация текущей даты
    const today = new Date();
    let currentDate = new Date();
    let selectedDate = new Date();
    let currentSelectedDay = today.getDay(); // 0-6 (0 - воскресенье)

    // Цвета для привычек
    const habitColors = [
        { name: 'Красный', value: 'bg-red-100 text-red-800' },
        { name: 'Синий', value: 'bg-blue-100 text-blue-800' },
        { name: 'Зелёный', value: 'bg-green-100 text-green-800' },
        { name: 'Жёлтый', value: 'bg-yellow-100 text-yellow-800' },
        { name: 'Фиолетовый', value: 'bg-purple-100 text-purple-800' },
        { name: 'Розовый', value: 'bg-pink-100 text-pink-800' },
    ];

    // Функция для отображения календаря
    function renderCalendar() {
        const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
        const calendar = document.getElementById('week-calendar');
        calendar.innerHTML = '';

        // Получаем понедельник текущей недели
        const monday = new Date(currentDate);
        monday.setDate(currentDate.getDate() - currentDate.getDay() + (currentDate.getDay() === 0 ? -6 : 1));

        // Создаем дни недели
        for (let i = 0; i < 7; i++) {
            const day = new Date(monday);
            day.setDate(monday.getDate() + i);

            const dayElement = document.createElement('div');
            dayElement.className = `flex flex-col items-center p-2 rounded-lg cursor-pointer transition ${isSameDay(day, selectedDate) ? 'bg-indigo-100' : 'hover:bg-gray-100'}`;
            dayElement.onclick = () => {
                selectDate(day);
                currentSelectedDay = day.getDay(); // Обновляем выбранный день
            };

            dayElement.innerHTML = `
                <div class="text-sm font-medium">${weekDays[i]}</div>
                <div class="text-lg ${isSameDay(day, today) ? 'font-bold text-indigo-600' : ''}">${day.getDate()}</div>
            `;

            calendar.appendChild(dayElement);
        }

        // Обновляем список привычек для выбранного дня
        updateHabitsList();
    }

    // Функция выбора даты
    function selectDate(date) {
        selectedDate = date;
        renderCalendar();
    }

    // Функция проверки совпадения дат
    function isSameDay(d1, d2) {
        return d1.getDate() === d2.getDate() &&
               d1.getMonth() === d2.getMonth() &&
               d1.getFullYear() === d2.getFullYear();
    }

    // Функция обновления списка привычек
    function updateHabitsList() {
        const habitsList = document.getElementById('habits-list');
        const dayOfWeek = selectedDate.getDay();

        // Запрос к API для получения привычек на выбранный день
        fetch(`/habits/get_by_day/?day=${dayOfWeek}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (data.habits.length === 0) {
                        habitsList.innerHTML = `
                            <div class="text-center py-8 text-gray-500">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-2 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <p>На этот день нет запланированных привычек</p>
                            </div>
                        `;
                    } else {
                        habitsList.innerHTML = data.habits.map(habit => createHabitElement(habit, false).outerHTML).join('');
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }

    // Функция загрузки всех привычек пользователя
    function loadAllHabits() {
        fetch('/habits/get_all/')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const allHabitsList = document.getElementById('all-habits-list');
                    allHabitsList.innerHTML = data.habits.map(habit => createHabitElement(habit, true).outerHTML).join('');
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }

    // Создание элемента привычки (только категория окрашивается)
    function createHabitElement(habit, withDaysInfo) {
        const element = document.createElement('div');
        element.className = 'p-4 hover:bg-gray-50 transition bg-white border-b';
        element.dataset.habitId = habit.id;

        // Получаем дни недели для привычки
        const daysMap = {0: 'Вс', 1: 'Пн', 2: 'Вт', 3: 'Ср', 4: 'Чт', 5: 'Пт', 6: 'Сб'};
        const activeDays = habit.schedule_days ? habit.schedule_days.map(day => daysMap[day]) : [];

        let daysHtml = '';
        if (withDaysInfo && activeDays.length > 0) {
            daysHtml = `<div class="mt-1 text-xs text-gray-500">Дни: ${activeDays.join(', ')}</div>`;
        }

        element.innerHTML = `
            <div class="flex justify-between items-start">
                <div>
                    <h3 class="font-medium">${habit.name}</h3>
                    <p class="text-sm text-gray-600">${habit.description || ''}</p>
                    ${daysHtml}
                </div>
                <div class="flex items-center space-x-2">
                    <button class="text-gray-400 hover:text-indigo-600 edit-habit" data-id="${habit.id}">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                        </svg>
                    </button>
                    <button class="text-gray-400 hover:text-red-600 delete-habit" data-id="${habit.id}">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                        </svg>
                    </button>
                </div>
            </div>
            <div class="mt-2 flex items-center justify-between">
                <span class="text-xs px-2 py-1 rounded-full ${habit.color_class}">
                    ${habit.category_display || habit.category}
                </span>
                <span class="text-xs text-gray-500">${habit.days_goal} дней</span>
            </div>
        `;

        return element;
    }

    // Функции для модального окна
    function openModal() {
        document.getElementById('modal').classList.remove('hidden');
        renderColorOptions();
    }

    function closeModal() {
        document.getElementById('modal').classList.add('hidden');
        document.getElementById('habit-form').reset();
        document.getElementById('habit-id').value = '';
    }

    // Функция отображения вариантов цвета
    function renderColorOptions() {
        const container = document.getElementById('color-options');
        container.innerHTML = '';

        habitColors.forEach(color => {
            const colorElement = document.createElement('div');
            colorElement.className = `flex items-center space-x-2 p-2 rounded-lg cursor-pointer hover:bg-gray-100`;
            colorElement.onclick = () => selectColor(color.value);

            colorElement.innerHTML = `
                <div class="w-6 h-6 rounded-full ${color.value.split(' ')[0]}"></div>
                <span>${color.name}</span>
            `;

            container.appendChild(colorElement);
        });
    }

    // Функция выбора цвета
    function selectColor(colorClass) {
    const colorInput = document.getElementById('color');
    const selectedColor = document.getElementById('selected-color');

    if (!colorInput || !selectedColor) {
        console.warn('Цветовой input или индикатор не найден!');
        return;
    }

    colorInput.value = colorClass;
    selectedColor.className = `w-6 h-6 rounded-full ${colorClass}`;
}


    // Генерация случайной привычки
    function generateHabit() {
        const categories = ['health', 'productivity', 'learning', 'relationships', 'finance'];
        const healthHabits = ['Пить воду', 'Утренняя зарядка', '10 000 шагов', 'Медитация'];
        const productivityHabits = ['Планирование дня', 'Уборка рабочего стола', 'Ведение дневника'];
        const developmentHabits = ['Чтение книги', 'Изучение языка', 'Просмотр курса'];
        const relationsHabits = ['Звонок родителям', 'Свидание', 'Встреча с друзьями'];
        const financeHabits = ['Учет расходов', 'Инвестирование', 'Анализ бюджета'];

        const category = categories[Math.floor(Math.random() * categories.length)];
        let habitName = '';

        switch(category) {
            case 'health': habitName = healthHabits[Math.floor(Math.random() * healthHabits.length)]; break;
            case 'productivity': habitName = productivityHabits[Math.floor(Math.random() * productivityHabits.length)]; break;
            case 'learning': habitName = developmentHabits[Math.floor(Math.random() * developmentHabits.length)]; break;
            case 'relationships': habitName = relationsHabits[Math.floor(Math.random() * relationsHabits.length)]; break;
            case 'finance': habitName = financeHabits[Math.floor(Math.random() * financeHabits.length)]; break;
        }

        document.getElementById('name').value = habitName;
        document.getElementById('category').value = category;
        document.getElementById('description').value = 'Описание моей новой привычки';
        document.getElementById('days_goal').value = Math.floor(Math.random() * 90) + 10;

        // Выбираем случайный цвет
        const randomColor = habitColors[Math.floor(Math.random() * habitColors.length)];
        selectColor(randomColor.value);
    }

    // Обработчик отправки формы
    document.getElementById('habit-form').addEventListener('submit', function(e) {
        e.preventDefault();
        saveHabit();
    });


    // Функция сохранения привычки
   function saveHabit() {
    const form = document.getElementById('habit-form');

    const habitData = {
        habit_id: document.getElementById('habit-id').value,
        name: document.getElementById('name').value,
        category: document.getElementById('category').value,
        description: document.getElementById('description').value,
        days_goal: document.getElementById('days_goal').value,
        reminder: document.getElementById('reminder').checked,
        color_class: document.getElementById('color').value,
        schedule_days: Array.from(document.querySelectorAll('input[name="days"]:checked')).map(cb => cb.value)
    };

    fetch('/habits/save/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(habitData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Привычка сохранена!', data.habit);
            addHabitToAllHabitsList(data.habit);
            addHabitToSelectedDayList(data.habit);
            closeModal();
        } else {
            console.error('Ошибка сохранения:', data.error);
        }
    })
    .catch(error => {
        console.error('Ошибка запроса:', error);
    });
}




    // Добавление привычки в список "Все ваши привычки"
    function addHabitToAllHabitsList(habit) {
        const allHabitsList = document.getElementById('all-habits-list');
        if (allHabitsList) {
            const habitElement = createHabitElement(habit, true);
            allHabitsList.prepend(habitElement);
        }
    }

    // Добавление привычки в список "Привычки на выбранный день"
    function addHabitToSelectedDayList(habit) {
        const habitsList = document.getElementById('habits-list');
        const selectedDay = selectedDate.getDay();

        // Проверяем, есть ли выбранный день в расписании привычки
        const hasDay = habit.schedule_days ? habit.schedule_days.includes(selectedDay.toString()) : false;

        if (habitsList && hasDay) {
            const habitElement = createHabitElement(habit, false);

            // Если список пустой (с сообщением "нет привычек"), очищаем его
            if (habitsList.querySelector('.text-center')) {
                habitsList.innerHTML = '';
            }

            habitsList.prepend(habitElement);
        }
    }

    // Инициализация
    renderCalendar();
    loadAllHabits();

    // Назначение обработчиков событий
    document.getElementById('open-modal').addEventListener('click', openModal);
    document.getElementById('close-modal').addEventListener('click', closeModal);
    document.getElementById('generate-habit').addEventListener('click', generateHabit);

    // Глобальные функции для кнопок
    window.editHabit = function(id) {
        fetch(`/habits/get/${id}/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const habit = data.habit;
                    document.getElementById('name').value = habit.name;
                    document.getElementById('category').value = habit.category;
                    document.getElementById('days_goal').value = habit.days_goal;
                    document.getElementById('description').value = habit.description || '';
                    document.getElementById('habit-id').value = habit.id;
                    document.getElementById('reminder').checked = habit.reminder;

                    // Устанавливаем цвет
                    selectColor(habit.color_class);

                    // Устанавливаем выбранные дни
                    document.querySelectorAll('input[name="days"]').forEach(input => {
                        input.checked = habit.schedule_days ? habit.schedule_days.includes(input.value) : false;
                    });

                    openModal();
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    };

    window.deleteHabit = function(id) {
        if (confirm('Вы уверены, что хотите удалить эту привычку?')) {
            fetch(`/habits/delete/${id}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const allHabitsList = document.getElementById('all-habits-list');
                    const habitsList = document.getElementById('habits-list');

                    // Удаляем из обоих списков
                    allHabitsList.querySelector(`[data-habit-id="${id}"]`)?.remove();
                    habitsList.querySelector(`[data-habit-id="${id}"]`)?.remove();
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    };
});