import type { CookingTimer } from '$lib/types';

let timers = $state<CookingTimer[]>([]);
let intervalId: ReturnType<typeof setInterval> | null = null;

function generateId(): string {
	return crypto.randomUUID();
}

function startTicking() {
	if (intervalId) return;
	intervalId = setInterval(() => {
		timers = timers.map((timer) => {
			if (timer.isRunning && !timer.isPaused && timer.remaining > 0) {
				return { ...timer, remaining: timer.remaining - 1 };
			}
			if (timer.remaining === 0 && timer.isRunning) {
				playAlarm();
				return { ...timer, isRunning: false };
			}
			return timer;
		});

		if (!timers.some((t) => t.isRunning && !t.isPaused)) {
			stopTicking();
		}
	}, 1000);
}

function stopTicking() {
	if (intervalId) {
		clearInterval(intervalId);
		intervalId = null;
	}
}

function playAlarm() {
	if (typeof window !== 'undefined' && 'Notification' in window) {
		if (Notification.permission === 'granted') {
			new Notification('Timer Complete!', { body: 'Your cooking timer has finished.' });
		}
	}
	const audio = new Audio(
		'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2teleQQAf7LnzplUCi2I2++2bh8AIJLh/8GGOBMjmdv+sXgyDyqa2P2zbzQQJ5jY/bRuNBEnmNj9tG40ESeY2P20bjQRJ5jY/bRuNBEnmA=='
	);
	audio.play().catch(() => {});
}

export function getTimers(): CookingTimer[] {
	return timers;
}

export function addTimer(name: string, durationMinutes: number): string {
	const id = generateId();
	const durationSeconds = durationMinutes * 60;
	timers = [
		...timers,
		{
			id,
			name,
			duration: durationSeconds,
			remaining: durationSeconds,
			isRunning: false,
			isPaused: false
		}
	];
	return id;
}

export function startTimer(id: string) {
	timers = timers.map((t) => (t.id === id ? { ...t, isRunning: true, isPaused: false } : t));
	startTicking();
}

export function pauseTimer(id: string) {
	timers = timers.map((t) => (t.id === id ? { ...t, isPaused: true } : t));
}

export function resumeTimer(id: string) {
	timers = timers.map((t) => (t.id === id ? { ...t, isPaused: false } : t));
	startTicking();
}

export function resetTimer(id: string) {
	timers = timers.map((t) =>
		t.id === id ? { ...t, remaining: t.duration, isRunning: false, isPaused: false } : t
	);
}

export function removeTimer(id: string) {
	timers = timers.filter((t) => t.id !== id);
}

export function formatTime(seconds: number): string {
	const hrs = Math.floor(seconds / 3600);
	const mins = Math.floor((seconds % 3600) / 60);
	const secs = seconds % 60;
	if (hrs > 0) {
		return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
	}
	return `${mins}:${secs.toString().padStart(2, '0')}`;
}

export function requestNotificationPermission() {
	if (typeof window !== 'undefined' && 'Notification' in window) {
		Notification.requestPermission();
	}
}
