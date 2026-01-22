<script lang="ts">
	import { Card, CardContent, Modal } from '@mskalski/home-ui';
	import type { Collection } from '$lib/types';
	import { api } from '$lib/utils';
	import { onMount } from 'svelte';

	let collections: Collection[] = $state([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let showCreateModal = $state(false);
	let newName = $state('');
	let newDescription = $state('');
	let creating = $state(false);

	let editingId = $state<number | null>(null);
	let editName = $state('');
	let editDescription = $state('');

	onMount(async () => {
		await loadCollections();
	});

	async function loadCollections() {
		loading = true;
		error = null;
		try {
			collections = await api.get<Collection[]>('/collections');
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load collections';
		} finally {
			loading = false;
		}
	}

	async function handleCreate() {
		if (!newName.trim()) return;

		creating = true;
		try {
			const collection = await api.post<Collection>('/collections', {
				name: newName,
				description: newDescription || null
			});
			collections = [...collections, collection];
			showCreateModal = false;
			newName = '';
			newDescription = '';
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to create collection';
		} finally {
			creating = false;
		}
	}

	async function handleUpdate() {
		if (editingId === null || !editName.trim()) return;

		try {
			const updated = await api.put<Collection>(`/collections/${editingId}`, {
				name: editName,
				description: editDescription || null
			});
			collections = collections.map((c) => (c.id === editingId ? updated : c));
			editingId = null;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to update collection';
		}
	}

	async function handleDelete(id: number) {
		if (!confirm('Delete this collection? Recipes will not be deleted.')) return;

		try {
			await api.delete(`/collections/${id}`);
			collections = collections.filter((c) => c.id !== id);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to delete collection';
		}
	}
</script>

<div class="page">
	<div class="page-header">
		<h1>Collections</h1>
		<button onclick={() => (showCreateModal = true)} class="btn btn-primary">
			New Collection
		</button>
	</div>

	{#if error}
		<div class="error-message">{error}</div>
	{/if}

	{#if loading}
		<div class="loading">Loading...</div>
	{:else if collections.length === 0}
		<div class="empty-state">
			No collections yet. Create one to organize your recipes!
		</div>
	{:else}
		<div class="collection-grid">
			{#each collections as collection}
				<Card>
					<CardContent>
						{#if editingId === collection.id}
							<div class="edit-form">
								<input
									type="text"
									bind:value={editName}
									class="input"
									placeholder="Collection name"
								/>
								<textarea
									bind:value={editDescription}
									class="input textarea"
									rows="2"
									placeholder="Description (optional)"
								></textarea>
								<div class="edit-actions">
									<button onclick={handleUpdate} class="btn btn-success">Save</button>
									<button onclick={() => (editingId = null)} class="btn btn-secondary">Cancel</button>
								</div>
							</div>
						{:else}
							<a href="/collections/{collection.id}" class="collection-link">
								<h2 class="collection-title">{collection.name}</h2>
								{#if collection.description}
									<p class="collection-description">{collection.description}</p>
								{/if}
								<p class="collection-count">
									{collection.recipe_count} recipe{collection.recipe_count !== 1 ? 's' : ''}
								</p>
							</a>
							<div class="collection-actions">
								<button
									onclick={() => {
										editingId = collection.id;
										editName = collection.name;
										editDescription = collection.description || '';
									}}
									class="btn btn-secondary btn-sm"
								>
									Edit
								</button>
								<button onclick={() => handleDelete(collection.id)} class="btn btn-danger btn-sm">
									Delete
								</button>
							</div>
						{/if}
					</CardContent>
				</Card>
			{/each}
		</div>
	{/if}
</div>

<Modal
	open={showCreateModal}
	title="New Collection"
	onCancel={() => {
		showCreateModal = false;
		newName = '';
		newDescription = '';
	}}
	onConfirm={handleCreate}
	confirmText={creating ? 'Creating...' : 'Create'}
	confirmDisabled={creating || !newName.trim()}
>
	<div class="modal-form">
		<div class="form-group">
			<label for="name">Name *</label>
			<input
				id="name"
				type="text"
				bind:value={newName}
				class="input"
				placeholder="e.g., Weeknight Dinners"
			/>
		</div>
		<div class="form-group">
			<label for="description">Description</label>
			<textarea
				id="description"
				bind:value={newDescription}
				class="input textarea"
				rows="3"
				placeholder="Optional description..."
			></textarea>
		</div>
	</div>
</Modal>

<style>
	.page {
		display: flex;
		flex-direction: column;
		gap: var(--size-6);
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.page-header h1 {
		font-size: var(--font-size-6);
		font-weight: var(--font-weight-8);
		margin: 0;
	}

	.btn {
		padding: var(--size-2) var(--size-4);
		border-radius: var(--radius-2);
		font-size: var(--font-size-1);
		font-weight: var(--font-weight-6);
		cursor: pointer;
		text-decoration: none;
		transition: all 0.2s;
		border: none;
	}

	.btn-sm {
		padding: var(--size-1) var(--size-3);
		font-size: var(--font-size-0);
	}

	.btn-primary {
		background: var(--color-primary);
		color: var(--nord6);
	}

	.btn-primary:hover {
		background: var(--nord9);
	}

	.btn-secondary {
		background: var(--color-accent);
		color: var(--color-text);
	}

	.btn-secondary:hover {
		background: var(--color-border);
	}

	.btn-success {
		background: var(--color-success);
		color: var(--nord6);
	}

	.btn-success:hover {
		opacity: 0.9;
	}

	.btn-danger {
		background: rgba(191, 97, 106, 0.2);
		color: var(--color-error);
	}

	.btn-danger:hover {
		background: rgba(191, 97, 106, 0.3);
	}

	.loading {
		text-align: center;
		padding: var(--size-8) 0;
	}

	.error-message {
		background: rgba(191, 97, 106, 0.2);
		color: var(--color-error);
		padding: var(--size-4);
		border-radius: var(--radius-2);
	}

	.empty-state {
		text-align: center;
		padding: var(--size-8) 0;
		color: var(--color-text-muted);
	}

	.collection-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
		gap: var(--size-6);
	}

	.collection-link {
		display: block;
		text-decoration: none;
		color: inherit;
	}

	.collection-title {
		font-size: var(--font-size-4);
		font-weight: var(--font-weight-6);
		margin: 0;
		transition: color 0.2s;
	}

	.collection-link:hover .collection-title {
		color: var(--color-primary);
	}

	.collection-description {
		font-size: var(--font-size-1);
		color: var(--color-text-muted);
		margin: var(--size-1) 0 0 0;
	}

	.collection-count {
		font-size: var(--font-size-0);
		color: var(--color-text-muted);
		margin: var(--size-2) 0 0 0;
	}

	.collection-actions {
		display: flex;
		gap: var(--size-2);
		margin-top: var(--size-4);
	}

	.edit-form {
		display: flex;
		flex-direction: column;
		gap: var(--size-3);
	}

	.edit-actions {
		display: flex;
		gap: var(--size-2);
	}

	.input {
		width: 100%;
		padding: var(--size-2) var(--size-3);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-2);
		font-size: var(--font-size-1);
		background: var(--color-bg);
		color: var(--color-text);
	}

	.input:focus {
		outline: none;
		border-color: var(--color-primary);
	}

	.textarea {
		resize: vertical;
	}

	.modal-form {
		display: flex;
		flex-direction: column;
		gap: var(--size-4);
	}

	.form-group {
		display: flex;
		flex-direction: column;
		gap: var(--size-2);
	}

	.form-group label {
		font-size: var(--font-size-1);
		font-weight: var(--font-weight-6);
	}
</style>
