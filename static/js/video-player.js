/*!
 * KRONIK Video Player - Custom VideoJS Implementation
 * Version 1.0
 * 
 * Features:
 * - Multiple quality options
 * - Playback speed control
 * - Keyboard shortcuts
 * - Resume viewing
 * - Next video recommendations
 * - Viewing statistics
 * - Picture-in-Picture
 * - Custom theme that adapts to site theme
 */

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
    
    initPlayer() {
        // Базовые опции плеера
        const defaultOptions = {
            responsive: true,
            fluid: true,
            playbackRates: [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2],
            controlBar: {
                children: [
                    'playToggle',
                    'volumePanel',
                    'currentTimeDisplay',
                    'timeDivider',
                    'durationDisplay',
                    'progressControl',
                    'playbackRateMenuButton',
                    'qualitySelector',
                    'pictureInPictureToggle',
                    'fullscreenToggle'
                ]
            },
            plugins: {
                httpSourceSelector: {
                    default: 'auto'
                }
            }
        };

        javascriptCopy// Продолжение файла static/js/video-player.js

        // Объединяем пользовательские опции с дефолтными
        const playerOptions = { ...defaultOptions, ...this.options };
        
        // Инициализация видеоплеера
        this.player = videojs(this.playerElementId, playerOptions);
        
        // Активация плагинов
        this.player.qualityLevels();
        this.player.httpSourceSelector();
        
        // Запоминание последней позиции воспроизведения
        this.setupResumeFeature();
        
        // Настройка отслеживания просмотра
        this.setupWatchTracking();
        
        // Настройка горячих клавиш
        this.setupKeyboardShortcuts();
        
        // Настройка автовоспроизведения следующего видео
        this.setupNextVideoFeature();
    }
    
    setupResumeFeature() {
        const savedTime = localStorage.getItem(`kronik-video-time-${this.videoId}`);
        
        if (savedTime && parseFloat(savedTime) > 0 && parseFloat(savedTime) < this.player.duration() * 0.95) {
            // Показать диалог для продолжения просмотра
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
                if (this.player.el().contains(resumeElement)) {
                    resumeElement.remove();
                }
            }, 10000);
        }
        
        // Сохраняем позицию просмотра каждые 5 секунд
        this.saveTimeInterval = setInterval(() => {
            if (!this.player.paused() && this.player.currentTime() > 0) {
                localStorage.setItem(`kronik-video-time-${this.videoId}`, this.player.currentTime());
            }
        }, 5000);
        
        // Очистка при уничтожении плеера
        this.player.on('dispose', () => {
            clearInterval(this.saveTimeInterval);
        });
    }
    
    setupWatchTracking() {
        let videoWatched = false;
        let watchPercentage = 0;
        let lastUpdateTime = 0;
        
        this.player.on('timeupdate', () => {
            const currentTime = this.player.currentTime();
            const duration = this.player.duration();
            
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
                    
                    // AJAX запрос для сохранения статистики
                    if (this.options.trackWatchProgress) {
                        fetch('/api/video/track-progress', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': this.getCsrfToken()
                            },
                            body: JSON.stringify({
                                video_id: this.videoId,
                                progress: watchPercentage,
                                watched_duration: currentTime
                            })
                        }).catch(error => console.error('Error tracking progress:', error));
                    }
                }
            }
            
            // Отмечаем как просмотренное после 95%
            if (!videoWatched && watchPercentage >= 95) {
                videoWatched = true;
                console.log('Видео полностью просмотрено');
                
                // Аналитика полного просмотра
                if (this.options.trackWatchComplete) {
                    fetch('/api/video/complete-view', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': this.getCsrfToken()
                        },
                        body: JSON.stringify({
                            video_id: this.videoId
                        })
                    }).catch(error => console.error('Error tracking completion:', error));
                }
                
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
                    
                case '0': case '1': case '2': case '3': case '4':
                case '5': case '6': case '7': case '8': case '9':
                    // Числовые клавиши - перейти к проценту видео
                    const percent = parseInt(event.key) * 10;
                    this.player.currentTime(this.player.duration() * percent / 100);
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
        nextTitle = nextElement.querySelector(this.options.nextTitleSelector || '.title')?.textContent || 'Следующее видео';
        nextChannel = nextElement.querySelector(this.options.nextChannelSelector || '.channel')?.textContent || '';
        
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
    
    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
    
    isPlayerInViewport() {
        const rect = this.player.el().getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
}

// Экспортируем класс для использования
window.KronikPlayer = KronikPlayer;