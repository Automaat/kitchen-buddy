<script lang="ts">
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

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h1 class="text-3xl font-bold text-gray-900">Collections</h1>
		<button
			onclick={() => (showCreateModal = true)}
			class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
		>
			New Collection
		</button>
	</div>

	{#if error}
		<div class="bg-red-50 text-red-700 p-4 rounded-lg">{error}</div>
	{/if}

	{#if loading}
		<div class="text-center py-12">Loading...</div>
	{:else if collections.length === 0}
		<div class="text-center py-12 text-gray-500">
			No collections yet. Create one to organize your recipes!
		</div>
	{:else}
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
			{#each collections as collection}
				<div class="bg-white rounded-lg shadow-sm border p-6">
					{#if editingId === collection.id}
						<div class="space-y-3">
							<input
								type="text"
								bind:value={editName}
								class="w-full px-3 py-2 border rounded-lg"
								placeholder="Collection name"
							/>
							<textarea
								bind:value={editDescription}
								class="w-full px-3 py-2 border rounded-lg"
								rows="2"
								placeholder="Description (optional)"
							></textarea>
							<div class="flex gap-2">
								<button
									onclick={handleUpdate}
									class="px-3 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200"
								>
									Save
								</button>
								<button
									onclick={() => (editingId = null)}
									class="px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
								>
									Cancel
								</button>
							</div>
						</div>
					{:else}
						<a href="/collections/{collection.id}" class="block">
							<h2 class="text-xl font-semibold hover:text-blue-600">{collection.name}</h2>
							{#if collection.description}
								<p class="text-gray-600 text-sm mt-1">{collection.description}</p>
							{/if}
							<p class="text-gray-500 text-sm mt-2">
								{collection.recipe_count} recipe{collection.recipe_count !== 1 ? 's' : ''}
							</p>
						</a>
						<div class="flex gap-2 mt-4">
							<button
								onclick={() => {
									editingId = collection.id;
									editName = collection.name;
									editDescription = collection.description || '';
								}}
								class="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
							>
								Edit
							</button>
							<button
								onclick={() => handleDelete(collection.id)}
								class="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200"
							>
								Delete
							</button>
						</div>
					{/if}
				</div>
			{/each}
		</div>
	{/if}
</div>

{#if showCreateModal}
	<div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
		<div class="bg-white rounded-lg p-6 w-full max-w-md">
			<h2 class="text-xl font-semibold mb-4">New Collection</h2>
			<div class="space-y-4">
				<div>
					<label for="name" class="block text-sm font-medium text-gray-700 mb-1">Name *</label>
					<input
						id="name"
						type="text"
						bind:value={newName}
						class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
						placeholder="e.g., Weeknight Dinners"
					/>
				</div>
				<div>
					<label for="description" class="block text-sm font-medium text-gray-700 mb-1">
						Description
					</label>
					<textarea
						id="description"
						bind:value={newDescription}
						class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
						rows="3"
						placeholder="Optional description..."
					></textarea>
				</div>
			</div>
			<div class="flex gap-4 mt-6">
				<button
					onclick={handleCreate}
					disabled={creating || !newName.trim()}
					class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
				>
					{creating ? 'Creating...' : 'Create'}
				</button>
				<button
					onclick={() => {
						showCreateModal = false;
						newName = '';
						newDescription = '';
					}}
					class="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
				>
					Cancel
				</button>
			</div>
		</div>
	</div>
{/if}
