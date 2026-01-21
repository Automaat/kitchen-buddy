import { describe, it, expect } from 'vitest';
import { toISODate, addDays, getWeekDays } from './date';

describe('date utils', () => {
	it('toISODate returns YYYY-MM-DD format', () => {
		const date = new Date('2024-03-15T12:00:00Z');
		expect(toISODate(date)).toBe('2024-03-15');
	});

	it('addDays adds correct number of days', () => {
		const date = new Date('2024-03-15');
		const result = addDays(date, 5);
		expect(result.getDate()).toBe(20);
	});

	it('getWeekDays returns 7 days', () => {
		const start = new Date('2024-03-11');
		const days = getWeekDays(start);
		expect(days).toHaveLength(7);
	});
});
