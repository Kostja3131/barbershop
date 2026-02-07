document.addEventListener('DOMContentLoaded', function() {
    // Инициализация datepicker
    flatpickr("#datepicker", {
        locale: "ru",
        minDate: "today",
        maxDate: new Date().fp_incr(30),
        disable: [function(date) { return (date.getDay() === 0); }] // Вс - выходной
    });
    
    const form = document.getElementById('booking-form');
    const steps = document.querySelectorAll('.form-step');
    const nextBtns = document.querySelectorAll('.next-step');
    const prevBtns = document.querySelectorAll('.prev-step');
    let currentStep = 0;
    
    function showStep(stepIndex) {
        steps.forEach((step, index) => {
            step.classList.toggle('active', index === stepIndex);
        });
        currentStep = stepIndex;
    }
    
    nextBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            if (validateStep(currentStep)) {
                showStep(currentStep + 1);
                if (currentStep === 2) { loadTimeSlots(); }
            }
        });
    });
    
    prevBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            showStep(currentStep - 1);
        });
    });
    
    function validateStep(stepIndex) {
        if (stepIndex === 0 && !form.querySelector('input[name="service"]:checked')) {
            alert('Выберите услугу'); return false;
        }
        if (stepIndex === 1 && !form.querySelector('input[name="barber"]:checked')) {
            alert('Выберите барбера'); return false;
        }
        if (stepIndex === 2 && (!form.querySelector('#datepicker').value || !form.querySelector('.time-slot.selected'))) {
            alert('Выберите дату и время'); return false;
        }
        return true;
    }
    
    function loadTimeSlots() {
        const timeSlotsContainer = document.getElementById('time-slots');
        const timeInput = document.getElementById('selected-time'); // Скрытое поле
        timeSlotsContainer.innerHTML = '';
        
        const availableTimes = ['10:00', '11:00', '12:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00'];
        
        availableTimes.forEach(time => {
            const timeSlot = document.createElement('div');
            timeSlot.className = 'time-slot';
            timeSlot.textContent = time;
            timeSlot.addEventListener('click', function() {
                document.querySelectorAll('.time-slot').forEach(slot => slot.classList.remove('selected'));
                this.classList.add('selected');
                timeInput.value = time; // ЗАПИСЫВАЕМ ВРЕМЯ ДЛЯ FLASK
            });
            timeSlotsContainer.appendChild(timeSlot);
        });
    }
    
    // ОТПРАВКА НА СЕРВЕР (FLASK)
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);

        fetch('/booking.html', {
            method: 'POST',
            body: formData
        })
        .then(response => response.text())
        .then(data => {
            if (data === "SUCCESS") {
                // Заполняем экран успеха
                document.getElementById('success-service').textContent = form.querySelector('input[name="service"]:checked').value;
                document.getElementById('success-barber').textContent = form.querySelector('input[name="barber"]:checked').value;
                document.getElementById('success-date').textContent = form.querySelector('#datepicker').value;
                document.getElementById('success-time').textContent = document.getElementById('selected-time').value;

                form.style.display = 'none';
                document.getElementById('booking-success').style.display = 'block';
            } else {
                alert("Ошибка при записи: " + data);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert("Произошла ошибка соединения с сервером");
        });
    });
    
    showStep(0);
});