/*!
 * KRONIK Video Player - Custom VideoJS Implementation
 * Version 1.0
 */

// Убеждаемся, что переменная KronikPlayer не объявлена ранее
if (typeof KronikPlayer === 'undefined') {
    // Определяем класс KronikPlayer в глобальной области видимости
    window.KronikPlayer = class KronikPlayer {
        constructor(elementId, options = {}) {
            this.playerElementId = elementId;
            this.options = options;
            this.player = null;
            this.videoId = options.videoId || 'video-' + Math.random().toString(36).substr(2, 9);
            this.saveTimeInterval = null;
            
            // Инициализация
            this.initPlayer();
        }
        // Базовые опции плеера
        const defaultOptions = {
            responsive: true,
            fluid: true,
            playbackRates: [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2],
            controls: true,
            preload: 'auto',
            controlBar: {
                children: [
                    'playToggle',
                    'volumePanel',
                    'currentTimeDisplay',
                    'timeDivider',
                    'durationDisplay',
                    'progressControl',
                    'fullscreenToggle'
                ]
            }
        };

        // Объединяем пользовательские опции с дефолтными
        const playerOptions = { ...defaultOptions, ...this.options };
        
        // Инициализация видеоплеера
        if (typeof videojs !== 'undefined') {
            this.player = videojs(this.playerElementId, playerOptions);
            
            // Настройка отслеживания просмотра
            this.setupWatchTracking();
            
            // Настройка горячих клавиш
            this.setupKeyboardShortcuts();
            
            // Запоминание последней позиции воспроизведения
            this.setupResumeFeature();
            
            // Настройка автовоспроизведения следующего видео
            this.setupNextVideoFeature();
        } else {
            console.error('VideoJS не найден. Проверьте, что библиотека загружена.');
        }
    }
    
    setupResumeFeature() {
        if (!this.player) return;
        
        const savedTime = localStorage.getItem(`kronik-video-time-${this.videoId}`);
        
        if (savedTime && parseFloat(savedTime) > 0) {
            // Создаем диалог для продолжения просмотра
            const resumeElement = document.createElement('div');
            resumeElement.className = 'vjs-resume-overlay';
            resumeElement.innerHTML = `
                <div class="resume-message">
                    Продолжить просмотр с ${this.formatTime(parseFloat(savedTime))}?
                </div>
                <div class="resume-buttons">
                    <button class="resume-yes">Да</button>
                    <button class="resume-no">Нет</button>
                </div>
            `;
            
            this.player.el().appendChild(resumeElement);
            
            // Обработка кнопок
            resumeElement.querySelector('.resume-yes').addEventListener('click', () => {
                this.player.currentTime(parseFloat(savedTime));
                resumeElement.remove();
                this.player.play();
            });
            
            resumeElement.querySelector('.resume-no').addEventListener('click', () => {
                resumeElement.remove();
                localStorage.removeItem(`kronik-video-time-${this.videoId}`);
            });
            
            // Автоматически скрыть через 10 секунд если нет действий
            setTimeout(() => {
                if (resumeElement.parentNode) {
                    resumeElement.remove();
                }
            }, 10000);
        }
        
        // Сохраняем позицию просмотра каждые 5 секунд
        this.saveTimeInterval = setInterval(() => {
            if (this.player && !this.player.paused() && this.player.currentTime() > 0) {
                localStorage.setItem(`kronik-video-time-${this.videoId}`, this.player.currentTime());
            }
        }, 5000);
        
        // Очистка при уничтожении плеера
        this.player.on('dispose', () => {
            clearInterval(this.saveTimeInterval);
        });
    }
    
    setupWatchTracking() {
        if (!this.player) return;
        
        let videoWatched = false;
        let watchPercentage = 0;
        let lastUpdateTime = 0;
        
        this.player.on('timeupdate', () => {
            const currentTime = this.player.currentTime();
            const duration = this.player.duration();
            
            if (isNaN(duration)) return;
            
            // Обновляем не чаще, чем раз в секунду
            if (currentTime - lastUpdateTime < 1) {
                return;
            }
            lastUpdateTime = currentTime;
            
            const currentPercentage = Math.floor((currentTime / duration) * 100);
            
            // Обновляем процент просмотра
            if (currentPercentage > watchPercentage) {
                watchPercentage = currentPercentage;
                
                // Сохраняем статистику просмотра при достижении ключевых точек
                if ([25, 50, 75, 95].includes(watchPercentage)) {
                    console.log(`Просмотрено ${watchPercentage}%`);
                }
            }
            
            // Отмечаем как просмотренное после 95%
            if (!videoWatched && watchPercentage >= 95) {
                videoWatched = true;
                console.log('Видео полностью просмотрено');
                
                // Удаляем сохраненную позицию, т.к. видео просмотрено
                localStorage.removeItem(`kronik-video-time-${this.videoId}`);
            }
        });
        
        // При окончании видео
        this.player.on('ended', () => {
            videoWatched = true;
            localStorage.removeItem(`kronik-video-time-${this.videoId}`);
            
            if (this.options.showNextVideo) {
                this.showNextVideoRecommendation();
            }
        });
    }
    
    setupKeyboardShortcuts() {
        if (!this.player) return;
        
        const handleKeyDown = (event) => {
            // Если фокус на элементе ввода, игнорируем
            if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
                return;
            }
            
            // Если плеер не в фокусе, не реагируем
            if (!this.isPlayerInViewport()) {
                return;
            }
            
            switch(event.key) {
                case ' ':  // Пробел - пауза/воспроизведение
                    if (this.player.paused()) {
                        this.player.play();
                    } else {
                        this.player.pause();
                    }
                    event.preventDefault();
                    break;
                    
                case 'ArrowRight':  // Стрелка вправо - вперед на 10 секунд
                    this.player.currentTime(this.player.currentTime() + 10);
                    event.preventDefault();
                    break;
                    
                case 'ArrowLeft':  // Стрелка влево - назад на 10 секунд
                    this.player.currentTime(this.player.currentTime() - 10);
                    event.preventDefault();
                    break;
                    
                case 'ArrowUp':  // Стрелка вверх - увеличить громкость
                    let volume = this.player.volume() + 0.1;
                    if (volume > 1) volume = 1;
                    this.player.volume(volume);
                    if (this.player.muted()) this.player.muted(false);
                    event.preventDefault();
                    break;
                    
                case 'ArrowDown':  // Стрелка вниз - уменьшить громкость
                    let vol = this.player.volume() - 0.1;
                    if (vol < 0) vol = 0;
                    this.player.volume(vol);
                    event.preventDefault();
                    break;
                    
                case 'f':  // F - полный экран
                    if (this.player.isFullscreen()) {
                        this.player.exitFullscreen();
                    } else {
                        this.player.requestFullscreen();
                    }
                    event.preventDefault();
                    break;
                    
                case 'm':  // M - отключение звука
                    this.player.muted(!this.player.muted());
                    event.preventDefault();
                    break;
            }
        };
        
        // Добавляем обработчик клавиш
        document.addEventListener('keydown', handleKeyDown);
        
        // Удаляем обработчик при уничтожении плеера
        this.player.on('dispose', () => {
            document.removeEventListener('keydown', handleKeyDown);
        });
    }
    
    setupNextVideoFeature() {
        if (!this.player) return;
        
        // Настраиваем только если задан колбэк или селектор следующего видео
        if (!this.options.nextVideoSelector && !this.options.onNextVideo) {
            return;
        }
        
        this.player.on('ended', () => {
            // Если задан колбэк, используем его
            if (typeof this.options.onNextVideo === 'function') {
                this.options.onNextVideo();
                return;
            }
            
            // Иначе ищем следующее видео по селектору
            const nextVideoElement = document.querySelector(this.options.nextVideoSelector);
            if (!nextVideoElement) return;
            
            this.showNextVideoRecommendation(nextVideoElement);
        });
    }
    
    showNextVideoRecommendation(nextElement) {
        if (!this.player) return;
        
        if (!nextElement && this.options.nextVideoSelector) {
            nextElement = document.querySelector(this.options.nextVideoSelector);
        }
        
        if (!nextElement) return;
        
        // Получаем данные для следующего видео
        let nextVideoLink, nextThumbnail, nextTitle, nextChannel;
        
        if (typeof nextElement.onclick === 'function') {
            // Пытаемся извлечь URL из атрибута onclick
            const onclickStr = nextElement.onclick.toString();
            const match = onclickStr.match(/window\.location\.href\s*=\s*['"]([^'"]+)['"]/);
            if (match) nextVideoLink = match[1];
        } else if (nextElement.getAttribute('data-href')) {
            nextVideoLink = nextElement.getAttribute('data-href');
        } else if (nextElement.getAttribute('href')) {
            nextVideoLink = nextElement.getAttribute('href');
        }
        
        // Если не нашли ссылку, не показываем рекомендацию
        if (!nextVideoLink) return;
        
        // Получаем данные из элемента
        nextThumbnail = nextElement.querySelector('img')?.outerHTML || '';
        nextTitle = nextElement.querySelector(this.options.nextTitleSelector || '.related-title')?.textContent || 'Следующее видео';
        nextChannel = nextElement.querySelector(this.options.nextChannelSelector || '.related-channel')?.textContent || '';
        
        // Создаем и отображаем элемент с рекомендацией
        const nextOverlay = document.createElement('div');
        nextOverlay.className = 'vjs-next-overlay';
        nextOverlay.innerHTML = `
            <div class="next-container">
                <div class="next-message">Следующее видео через <span class="countdown">10</span></div>
                <div class="next-thumbnail">${nextThumbnail}</div>
                <div class="next-info">
                    <div class="next-title">${nextTitle}</div>
                    ${nextChannel ? `<div class="next-channel">${nextChannel}</div>` : ''}
                </div>
                <div class="next-buttons">
                    <button class="next-play">Смотреть сейчас</button>
                    <button class="next-cancel">Отмена</button>
                </div>
            </div>
        `;
        
        this.player.el().appendChild(nextOverlay);
        
        // Обратный отсчет
        let countdown = 10;
        const countdownElement = nextOverlay.querySelector('.countdown');
        
        const countdownInterval = setInterval(() => {
            countdown--;
            countdownElement.textContent = countdown;
            
            if (countdown <= 0) {
                clearInterval(countdownInterval);
                window.location.href = nextVideoLink;
            }
        }, 1000);
        
        // Обработка кнопок
        nextOverlay.querySelector('.next-play').addEventListener('click', () => {
            clearInterval(countdownInterval);
            window.location.href = nextVideoLink;
        });
        
        nextOverlay.querySelector('.next-cancel').addEventListener('click', () => {
            clearInterval(countdownInterval);
            nextOverlay.remove();
        });
    }
    
    // Вспомогательные методы
    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
    }
    
    isPlayerInViewport() {
        if (!this.player) return false;
        
        const rect = this.player.el().getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
}

window.KronikPlayer = KronikPlayer;