const BASE_URL = '/api';

async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
	const response = await fetch(`${BASE_URL}${endpoint}`, {
		headers: {
			'Content-Type': 'application/json',
			...options.headers
		},
		...options
	});

	if (!response.ok) {
		const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
		throw new Error(error.detail || `HTTP ${response.status}`);
	}

	if (response.status === 204) {
		return undefined as T;
	}

	return response.json();
}

export const api = {
	get: <T>(endpoint: string) => fetchApi<T>(endpoint),
	post: <T>(endpoint: string, data?: unknown) =>
		fetchApi<T>(endpoint, { method: 'POST', body: data ? JSON.stringify(data) : undefined }),
	put: <T>(endpoint: string, data: unknown) =>
		fetchApi<T>(endpoint, { method: 'PUT', body: JSON.stringify(data) }),
	delete: <T>(endpoint: string) => fetchApi<T>(endpoint, { method: 'DELETE' })
};

export async function uploadImage(recipeId: number, file: File, isPrimary = false): Promise<void> {
	const formData = new FormData();
	formData.append('file', file);

	const response = await fetch(
		`${BASE_URL}/recipes/${recipeId}/images?is_primary=${isPrimary}`,
		{
			method: 'POST',
			body: formData
		}
	);

	if (!response.ok) {
		const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
		throw new Error(error.detail);
	}
}

export function getImageUrl(imageId: number | null): string | null {
	if (!imageId) return null;
	return `${BASE_URL}/images/${imageId}`;
}
