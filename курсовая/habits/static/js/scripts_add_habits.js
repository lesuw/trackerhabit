document.addEventListener('DOMContentLoaded', function() {
// Инициализация текущей даты
const today = new Date();
let currentDate = new Date();
let selectedDate = new Date();

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
        dayElement.onclick = () => selectDate(day);

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
    const habits = getHabitsForDate(selectedDate);

    if (habits.length === 0) {
        habitsList.innerHTML = `
            <div class="text-center py-8 text-gray-500">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-2 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p>На этот день нет запланированных привычек</p>
            </div>
        `;
    } else {
        habitsList.innerHTML = habits.map(habit => `
            <div class="flex items-center justify-between p-4 border-b">
                <div>
                    <h3 class="font-medium">${habit.name}</h3>
                    <p class="text-sm text-gray-500">${habit.category} • ${habit.daysGoal} дней</p>
                </div>
                <button class="text-indigo-600 hover:text-indigo-800">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                    </svg>
                </button>
            </div>
        `).join('');
    }
}

// Функция получения привычек для даты (заглушка)
function getHabitsForDate(date) {
    // В реальном приложении здесь будет запрос к API
    if (isSameDay(date, today)) {
        return [
            { name: 'Утренняя зарядка', category: 'Здоровье', daysGoal: 30 },
            { name: 'Чтение книги', category: 'Развитие', daysGoal: 21 }
        ];
    }
    return [];
}

// Функция получения всех привычек пользователя (заглушка)
function getAllHabits() {
    return [
        { id: 1, name: 'Утренняя зарядка', category: 'Здоровье', color: 'bg-red-100 text-red-800', daysGoal: 30 },
        { id: 2, name: 'Чтение книги', category: 'Развитие', color: 'bg-blue-100 text-blue-800', daysGoal: 21 },
        { id: 3, name: 'Медитация', category: 'Здоровье', color: 'bg-green-100 text-green-800', daysGoal: 60 },
        { id: 4, name: 'Планирование дня', category: 'Продуктивность', color: 'bg-yellow-100 text-yellow-800', daysGoal: 90 },
        { id: 5, name: 'Учёт расходов', category: 'Финансы', color: 'bg-purple-100 text-purple-800', daysGoal: 365 }
    ];
}

// Функция отображения всех привычек
function renderAllHabits() {
    const allHabitsList = document.getElementById('all-habits-list');
    const habits = getAllHabits();

    allHabitsList.innerHTML = habits.map(habit => `
        <div class="flex items-center justify-between p-3 border-b hover:bg-gray-50">
            <div class="flex items-center space-x-3">
                <span class="${habit.color} px-2 py-1 rounded-full text-xs font-medium">${habit.category}</span>
                <span>${habit.name}</span>
                <span class="text-xs text-gray-500">${habit.daysGoal} дн.</span>
            </div>
            <div class="flex space-x-2">
                <button class="text-gray-500 hover:text-blue-600 transition" onclick="editHabit(${habit.id})">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                    </svg>
                </button>
                <button class="text-gray-500 hover:text-red-600 transition" onclick="deleteHabit(${habit.id})">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                    </svg>
                </button>
            </div>
        </div>
    `).join('');
}

// Функции для модального окна
function openModal() {
    document.getElementById('modal').classList.remove('hidden');
    renderColorOptions();
}

function closeModal() {
    document.getElementById('modal').classList.add('hidden');
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
    document.getElementById('selected-color').className = `w-6 h-6 rounded-full ${colorClass.split(' ')[0]}`;
    document.getElementById('selected-color-value').value = colorClass;
    document.getElementById('color-options').classList.add('hidden');
}

// Генерация случайной привычки
function generateHabit() {
    const categories = ['Здоровье', 'Продуктивность', 'Развитие', 'Отношения', 'Финансы'];
    const healthHabits = ['Пить воду', 'Утренняя зарядка', '10 000 шагов', 'Медитация'];
    const productivityHabits = ['Планирование дня', 'Уборка рабочего стола', 'Ведение дневника'];
    const developmentHabits = ['Чтение книги', 'Изучение языка', 'Просмотр курса'];
    const relationsHabits = ['Звонок родителям', 'Свидание', 'Встреча с друзьями'];
    const financeHabits = ['Учет расходов', 'Инвестирование', 'Анализ бюджета'];

    const category = categories[Math.floor(Math.random() * categories.length)];
    let habitName = '';

    switch(category) {
        case 'Здоровье': habitName = healthHabits[Math.floor(Math.random() * healthHabits.length)]; break;
        case 'Продуктивность': habitName = productivityHabits[Math.floor(Math.random() * productivityHabits.length)]; break;
        case 'Развитие': habitName = developmentHabits[Math.floor(Math.random() * developmentHabits.length)]; break;
        case 'Отношения': habitName = relationsHabits[Math.floor(Math.random() * relationsHabits.length)]; break;
        case 'Финансы': habitName = financeHabits[Math.floor(Math.random() * financeHabits.length)]; break;
    }

    document.getElementById('habit-name').value = habitName;
    document.getElementById('habit-category').value = category.toLowerCase();
    document.getElementById('habit-description').value = 'Описание моей новой привычки';
    document.getElementById('habit-days-goal').value = Math.floor(Math.random() * 90) + 10;

    // Выбираем случайный цвет
    const randomColor = habitColors[Math.floor(Math.random() * habitColors.length)];
    selectColor(randomColor.value);
}

// Функции для работы с привычками
function editHabit(id) {
    // В реальном приложении здесь будет запрос к API
    const habit = getAllHabits().find(h => h.id === id);
    if (habit) {
        document.getElementById('habit-name').value = habit.name;
        document.getElementById('habit-category').value = habit.category.toLowerCase();
        document.getElementById('habit-days-goal').value = habit.daysGoal;
        selectColor(habit.color);
        openModal();
    }
}

function deleteHabit(id) {
    // В реальном приложении здесь будет запрос к API
    if (confirm('Вы уверены, что хотите удалить эту привычку?')) {
        alert(`Привычка с ID ${id} будет удалена`);
        renderAllHabits();
    }
}

// Инициализация
renderCalendar();
renderAllHabits();

// Назначение обработчиков событий
document.getElementById('open-modal').addEventListener('click', openModal);
document.getElementById('close-modal').addEventListener('click', closeModal);
document.getElementById('generate-habit').addEventListener('click', generateHabit);

// Глобальные функции для кнопок
window.editHabit = editHabit;
window.deleteHabit = deleteHabit;