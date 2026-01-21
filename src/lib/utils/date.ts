export function formatDate(date: Date | string): string {
	const d = typeof date === 'string' ? new Date(date) : date;
	return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
}

export function toISODate(date: Date): string {
	return date.toISOString().split('T')[0];
}

export function getWeekStart(date: Date): Date {
	const d = new Date(date);
	const day = d.getDay();
	const diff = d.getDate() - day + (day === 0 ? -6 : 1);
	d.setDate(diff);
	d.setHours(0, 0, 0, 0);
	return d;
}

export function getWeekEnd(date: Date): Date {
	const start = getWeekStart(date);
	const end = new Date(start);
	end.setDate(start.getDate() + 6);
	return end;
}

export function addDays(date: Date, days: number): Date {
	const result = new Date(date);
	result.setDate(result.getDate() + days);
	return result;
}

export function getWeekDays(startDate: Date): Date[] {
	return Array.from({ length: 7 }, (_, i) => addDays(startDate, i));
}
