import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { api, getImageUrl, uploadImage } from './api';

describe('api utils', () => {
	const mockFetch = vi.fn();

	beforeEach(() => {
		vi.stubGlobal('fetch', mockFetch);
	});

	afterEach(() => {
		vi.unstubAllGlobals();
		mockFetch.mockReset();
	});

	describe('api.get', () => {
		it('makes GET request with correct URL', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				status: 200,
				json: () => Promise.resolve({ data: 'test' })
			});

			const result = await api.get('/recipes');

			expect(mockFetch).toHaveBeenCalledWith('/api/recipes', {
				headers: { 'Content-Type': 'application/json' }
			});
			expect(result).toEqual({ data: 'test' });
		});

		it('throws on error response', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 404,
				json: () => Promise.resolve({ detail: 'Not found' })
			});

			await expect(api.get('/recipes/999')).rejects.toThrow('Not found');
		});

		it('handles error without detail', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 500,
				json: () => Promise.reject(new Error())
			});

			await expect(api.get('/recipes')).rejects.toThrow('Unknown error');
		});
	});

	describe('api.post', () => {
		it('makes POST request with JSON body', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				status: 201,
				json: () => Promise.resolve({ id: 1 })
			});

			const result = await api.post('/recipes', { title: 'Test' });

			expect(mockFetch).toHaveBeenCalledWith('/api/recipes', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ title: 'Test' })
			});
			expect(result).toEqual({ id: 1 });
		});

		it('makes POST request without body', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				status: 201,
				json: () => Promise.resolve({ id: 1 })
			});

			await api.post('/favorites/1');

			expect(mockFetch).toHaveBeenCalledWith('/api/favorites/1', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: undefined
			});
		});
	});

	describe('api.put', () => {
		it('makes PUT request with JSON body', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				status: 200,
				json: () => Promise.resolve({ id: 1, title: 'Updated' })
			});

			await api.put('/recipes/1', { title: 'Updated' });

			expect(mockFetch).toHaveBeenCalledWith('/api/recipes/1', {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ title: 'Updated' })
			});
		});
	});

	describe('api.delete', () => {
		it('makes DELETE request', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				status: 204
			});

			await api.delete('/recipes/1');

			expect(mockFetch).toHaveBeenCalledWith('/api/recipes/1', {
				method: 'DELETE',
				headers: { 'Content-Type': 'application/json' }
			});
		});

		it('returns undefined for 204 response', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				status: 204
			});

			const result = await api.delete('/recipes/1');

			expect(result).toBeUndefined();
		});
	});

	describe('getImageUrl', () => {
		it('returns URL for valid image ID', () => {
			expect(getImageUrl(123)).toBe('/api/images/123');
		});

		it('returns null for null image ID', () => {
			expect(getImageUrl(null)).toBeNull();
		});

		it('returns null for zero image ID', () => {
			expect(getImageUrl(0)).toBeNull();
		});
	});

	describe('uploadImage', () => {
		it('uploads image with FormData', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				status: 201
			});

			const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
			await uploadImage(1, file);

			expect(mockFetch).toHaveBeenCalledWith(
				'/api/recipes/1/images?is_primary=false',
				expect.objectContaining({
					method: 'POST',
					body: expect.any(FormData)
				})
			);
		});

		it('uploads image as primary', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				status: 201
			});

			const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
			await uploadImage(1, file, true);

			expect(mockFetch).toHaveBeenCalledWith(
				'/api/recipes/1/images?is_primary=true',
				expect.objectContaining({
					method: 'POST'
				})
			);
		});

		it('throws on upload error', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 400,
				json: () => Promise.resolve({ detail: 'Invalid image type' })
			});

			const file = new File(['test'], 'test.txt', { type: 'text/plain' });
			await expect(uploadImage(1, file)).rejects.toThrow('Invalid image type');
		});

		it('handles error without detail message', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 500,
				json: () => Promise.reject(new Error())
			});

			const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
			await expect(uploadImage(1, file)).rejects.toThrow('Upload failed');
		});
	});
});
