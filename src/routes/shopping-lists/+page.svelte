<script lang="ts">
	import type { ShoppingList } from '$lib/types';
	import { api, formatDate, toISODate, getWeekStart, addDays } from '$lib/utils';
	import { onMount } from 'svelte';

	let lists: ShoppingList[] = $state([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let showCreateModal = $state(false);
	let showGenerateModal = $state(false);
	let newListName = $state('');
	let generatingName = $state('');
	let startDate = $state(toISODate(getWeekStart(new Date())));
	let endDate = $state(toISODate(addDays(getWeekStart(new Date()), 6)));

	async function loadLists() {
		loading = true;
		error = null;
		try {
			lists = await api.get<ShoppingList[]>('/shopping-lists');
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load shopping lists';
		} finally {
			loading = false;
		}
	}

	onMount(loadLists);

	async function createList() {
		if (!newListName.trim()) return;
		try {
			await api.post('/shopping-lists', { name: newListName });
			newListName = '';
			showCreateModal = false;
			await loadLists();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to create list';
		}
	}

	async function generateList() {
		if (!generatingName.trim()) return;
		try {
			await api.post('/shopping-lists/generate', {
				name: generatingName,
				start_date: startDate,
				end_date: endDate
			});
			generatingName = '';
			showGenerateModal = false;
			await loadLists();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to generate list';
		}
	}

	async function deleteList(id: number) {
		if (!confirm('Delete this shopping list?')) return;
		try {
			await api.delete(`/shopping-lists/${id}`);
			await loadLists();
		} catch {
			/* ignore */
		}
	}

	function getProgress(list: ShoppingList): number {
		if (list.items.length === 0) return 0;
		return Math.round((list.items.filter((i) => i.is_checked).length / list.items.length) * 100);
	}
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h1 class="text-3xl font-bold text-gray-900">Shopping Lists</h1>
		<div class="flex gap-2">
			<button
				onclick={() => (showGenerateModal = true)}
				class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
			>
				Generate from Meals
			</button>
			<button
				onclick={() => (showCreateModal = true)}
				class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
			>
				New List
			</button>
		</div>
	</div>

	{#if error}
		<div class="bg-red-50 text-red-700 p-4 rounded-lg">{error}</div>
	{/if}

	{#if loading}
		<div class="text-center py-12">Loading...</div>
	{:else if lists.length === 0}
		<div class="text-center py-12 text-gray-500">
			No shopping lists yet. Create one or generate from your meal plan!
		</div>
	{:else}
		<div class="grid gap-4">
			{#each lists as list}
				<div class="bg-white p-4 rounded-lg shadow-sm border">
					<div class="flex items-center justify-between">
						<div>
							<a href="/shopping-lists/{list.id}" class="font-semibold text-lg hover:text-blue-600">
								{list.name}
							</a>
							{#if list.start_date && list.end_date}
								<p class="text-sm text-gray-500">
									{formatDate(list.start_date)} - {formatDate(list.end_date)}
								</p>
							{/if}
						</div>
						<div class="flex items-center gap-4">
							<div class="text-sm text-gray-600">
								{list.items.filter((i) => i.is_checked).length} / {list.items.length} items
							</div>
							<div class="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
								<div
									class="h-full bg-green-500 transition-all"
									style="width: {getProgress(list)}%"
								></div>
							</div>
							<a
								href="/shopping-lists/{list.id}"
								class="px-3 py-1 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200"
							>
								View
							</a>
							<button
								onclick={() => deleteList(list.id)}
								class="px-3 py-1 bg-red-100 text-red-700 rounded-lg hover:bg-red-200"
							>
								Delete
							</button>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

{#if showCreateModal}
	<div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
		<div class="bg-white p-6 rounded-lg shadow-xl max-w-md w-full mx-4">
			<h2 class="text-xl font-semibold mb-4">New Shopping List</h2>
			<form onsubmit={(e) => { e.preventDefault(); createList(); }} class="space-y-4">
				<div>
					<label for="listName" class="block text-sm font-medium text-gray-700 mb-1">Name</label>
					<input
						id="listName"
						type="text"
						bind:value={newListName}
						required
						class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
					/>
				</div>
				<div class="flex gap-2">
					<button
						type="submit"
						class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
					>
						Create
					</button>
					<button
						type="button"
						onclick={() => (showCreateModal = false)}
						class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
					>
						Cancel
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}

{#if showGenerateModal}
	<div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
		<div class="bg-white p-6 rounded-lg shadow-xl max-w-md w-full mx-4">
			<h2 class="text-xl font-semibold mb-4">Generate from Meal Plan</h2>
			<form onsubmit={(e) => { e.preventDefault(); generateList(); }} class="space-y-4">
				<div>
					<label for="genName" class="block text-sm font-medium text-gray-700 mb-1">Name</label>
					<input
						id="genName"
						type="text"
						bind:value={generatingName}
						placeholder="Weekly Shopping"
						required
						class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
					/>
				</div>
				<div class="grid grid-cols-2 gap-4">
					<div>
						<label for="startDate" class="block text-sm font-medium text-gray-700 mb-1">
							Start Date
						</label>
						<input
							id="startDate"
							type="date"
							bind:value={startDate}
							required
							class="w-full px-4 py-2 border rounded-lg"
						/>
					</div>
					<div>
						<label for="endDate" class="block text-sm font-medium text-gray-700 mb-1">
							End Date
						</label>
						<input
							id="endDate"
							type="date"
							bind:value={endDate}
							required
							class="w-full px-4 py-2 border rounded-lg"
						/>
					</div>
				</div>
				<div class="flex gap-2">
					<button
						type="submit"
						class="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
					>
						Generate
					</button>
					<button
						type="button"
						onclick={() => (showGenerateModal = false)}
						class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
					>
						Cancel
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}
