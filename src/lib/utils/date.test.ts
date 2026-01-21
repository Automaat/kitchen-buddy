import { describe, it, expect } from 'vitest';
import {
	toISODate,
	addDays,
	getWeekDays,
	formatDate,
	getWeekStart,
	getWeekEnd
} from './date';

describe('date utils', () => {
	describe('toISODate', () => {
		it('returns YYYY-MM-DD format', () => {
			const date = new Date('2024-03-15T12:00:00Z');
			expect(toISODate(date)).toBe('2024-03-15');
		});

		it('handles different months correctly', () => {
			const date = new Date('2024-01-05T00:00:00Z');
			expect(toISODate(date)).toBe('2024-01-05');
		});
	});

	describe('addDays', () => {
		it('adds correct number of days', () => {
			const date = new Date('2024-03-15');
			const result = addDays(date, 5);
			expect(result.getDate()).toBe(20);
		});

		it('handles month boundary', () => {
			const date = new Date('2024-03-30');
			const result = addDays(date, 5);
			expect(result.getMonth()).toBe(3); // April
			expect(result.getDate()).toBe(4);
		});

		it('handles negative days', () => {
			const date = new Date('2024-03-15');
			const result = addDays(date, -5);
			expect(result.getDate()).toBe(10);
		});

		it('does not mutate original date', () => {
			const date = new Date('2024-03-15');
			addDays(date, 5);
			expect(date.getDate()).toBe(15);
		});
	});

	describe('getWeekDays', () => {
		it('returns 7 days', () => {
			const start = new Date('2024-03-11');
			const days = getWeekDays(start);
			expect(days).toHaveLength(7);
		});

		it('returns consecutive days', () => {
			const start = new Date('2024-03-11');
			const days = getWeekDays(start);
			expect(days[0].getDate()).toBe(11);
			expect(days[6].getDate()).toBe(17);
		});
	});

	describe('formatDate', () => {
		it('formats Date object', () => {
			const date = new Date('2024-03-15');
			const result = formatDate(date);
			expect(result).toContain('Mar');
			expect(result).toContain('15');
		});

		it('formats string date', () => {
			const result = formatDate('2024-03-15');
			expect(result).toContain('Mar');
			expect(result).toContain('15');
		});

		it('includes weekday', () => {
			const date = new Date('2024-03-15'); // Friday
			const result = formatDate(date);
			expect(result).toContain('Fri');
		});
	});

	describe('getWeekStart', () => {
		it('returns Monday for mid-week date', () => {
			const date = new Date('2024-03-13'); // Wednesday
			const result = getWeekStart(date);
			expect(result.getDay()).toBe(1); // Monday
			expect(result.getDate()).toBe(11);
		});

		it('returns Monday for Monday', () => {
			const date = new Date('2024-03-11'); // Monday
			const result = getWeekStart(date);
			expect(result.getDate()).toBe(11);
		});

		it('returns previous Monday for Sunday', () => {
			const date = new Date('2024-03-17'); // Sunday
			const result = getWeekStart(date);
			expect(result.getDate()).toBe(11);
		});

		it('sets time to midnight', () => {
			const date = new Date('2024-03-15T15:30:00');
			const result = getWeekStart(date);
			expect(result.getHours()).toBe(0);
			expect(result.getMinutes()).toBe(0);
		});

		it('does not mutate original date', () => {
			const date = new Date('2024-03-15');
			getWeekStart(date);
			expect(date.getDate()).toBe(15);
		});
	});

	describe('getWeekEnd', () => {
		it('returns Sunday for mid-week date', () => {
			const date = new Date('2024-03-13'); // Wednesday
			const result = getWeekEnd(date);
			expect(result.getDay()).toBe(0); // Sunday
			expect(result.getDate()).toBe(17);
		});

		it('returns Sunday for Monday', () => {
			const date = new Date('2024-03-11'); // Monday
			const result = getWeekEnd(date);
			expect(result.getDate()).toBe(17);
		});

		it('returns same Sunday for Sunday', () => {
			const date = new Date('2024-03-17'); // Sunday
			const result = getWeekEnd(date);
			expect(result.getDate()).toBe(17);
		});

		it('is 6 days after week start', () => {
			const date = new Date('2024-03-15');
			const start = getWeekStart(date);
			const end = getWeekEnd(date);
			const diffDays = (end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24);
			expect(diffDays).toBe(6);
		});
	});
});
