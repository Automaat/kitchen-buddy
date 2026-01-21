<script lang="ts">
	import type { ShoppingList, ShoppingListItem, IngredientCategory, Ingredient } from '$lib/types';
	import { api, formatDate } from '$lib/utils';
	import { page } from '$app/stores';
	import { onMount } from 'svelte';

	let list: ShoppingList | null = $state(null);
	let ingredients: Ingredient[] = $state([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let showAddModal = $state(false);
	let newItemName = $state('');
	let newItemQuantity = $state('');
	let newItemUnit = $state('');
	let selectedIngredientId = $state<number | null>(null);

	const categoryOrder: IngredientCategory[] = [
		'produce',
		'dairy',
		'meat',
		'seafood',
		'bakery',
		'frozen',
		'pantry',
		'beverages',
		'condiments',
		'spices',
		'other'
	];

	const categoryLabels: Record<IngredientCategory, string> = {
		produce: 'Produce',
		dairy: 'Dairy',
		meat: 'Meat',
		seafood: 'Seafood',
		pantry: 'Pantry',
		frozen: 'Frozen',
		bakery: 'Bakery',
		beverages: 'Beverages',
		condiments: 'Condiments',
		spices: 'Spices',
		other: 'Other'
	};

	function groupByCategory(items: ShoppingListItem[]): Record<string, ShoppingListItem[]> {
		const groups: Record<string, ShoppingListItem[]> = {};
		for (const item of items) {
			const cat = item.category || 'other';
			if (!groups[cat]) groups[cat] = [];
			groups[cat].push(item);
		}
		return groups;
	}

	async function loadList() {
		loading = true;
		error = null;
		try {
			list = await api.get<ShoppingList>(`/shopping-lists/${$page.params.id}`);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load shopping list';
		} finally {
			loading = false;
		}
	}

	onMount(async () => {
		try {
			ingredients = await api.get<Ingredient[]>('/ingredients');
		} catch {
			/* ignore */
		}
		await loadList();
	});

	async function toggleItem(item: ShoppingListItem) {
		if (!list) return;
		try {
			const updated = await api.post<ShoppingListItem>(
				`/shopping-lists/${list.id}/items/${item.id}/toggle`
			);
			item.is_checked = updated.is_checked;
		} catch {
			/* ignore */
		}
	}

	async function deleteItem(item: ShoppingListItem) {
		if (!list) return;
		try {
			await api.delete(`/shopping-lists/${list.id}/items/${item.id}`);
			list.items = list.items.filter((i) => i.id !== item.id);
		} catch {
			/* ignore */
		}
	}

	async function addItem() {
		if (!list || (!newItemName.trim() && !selectedIngredientId)) return;
		try {
			const newItem = await api.post<ShoppingListItem>(`/shopping-lists/${list.id}/items`, {
				ingredient_id: selectedIngredientId,
				name: newItemName.trim() || null,
				quantity: newItemQuantity.trim() || null,
				unit: newItemUnit.trim() || null
			});
			list.items = [...list.items, newItem];
			newItemName = '';
			newItemQuantity = '';
			newItemUnit = '';
			selectedIngredientId = null;
			showAddModal = false;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to add item';
		}
	}

	function getProgress(): number {
		if (!list || list.items.length === 0) return 0;
		return Math.round((list.items.filter((i) => i.is_checked).length / list.items.length) * 100);
	}
</script>

{#if loading}
	<div class="text-center py-12">Loading...</div>
{:else if error}
	<div class="bg-red-50 text-red-700 p-4 rounded-lg">{error}</div>
{:else if list}
	<div class="max-w-2xl mx-auto space-y-6">
		<div class="flex items-center justify-between">
			<div>
				<a href="/shopping-lists" class="text-blue-600 hover:underline text-sm">
					← Back to lists
				</a>
				<h1 class="text-3xl font-bold text-gray-900">{list.name}</h1>
				{#if list.start_date && list.end_date}
					<p class="text-gray-500">
						{formatDate(list.start_date)} - {formatDate(list.end_date)}
					</p>
				{/if}
			</div>
			<button
				onclick={() => (showAddModal = true)}
				class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
			>
				Add Item
			</button>
		</div>

		<div class="bg-white p-4 rounded-lg shadow-sm border">
			<div class="flex items-center justify-between mb-2">
				<span class="text-sm text-gray-600">
					{list.items.filter((i) => i.is_checked).length} / {list.items.length} items checked
				</span>
				<span class="text-sm font-medium">{getProgress()}%</span>
			</div>
			<div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
				<div class="h-full bg-green-500 transition-all" style="width: {getProgress()}%"></div>
			</div>
		</div>

		{#if list.items.length === 0}
			<div class="text-center py-12 text-gray-500">
				No items in this list. Add some items to get started!
			</div>
		{:else}
			{@const grouped = groupByCategory(list.items)}
			{#each categoryOrder as category}
				{#if grouped[category]?.length}
					<div class="bg-white rounded-lg shadow-sm border overflow-hidden">
						<div class="px-4 py-2 bg-gray-50 border-b font-medium">
							{categoryLabels[category]}
						</div>
						<div class="divide-y">
							{#each grouped[category] as item}
								<div
									class="flex items-center gap-3 px-4 py-3 group {item.is_checked
										? 'bg-gray-50'
										: ''}"
								>
									<button
										onclick={() => toggleItem(item)}
										class="w-6 h-6 rounded-full border-2 flex items-center justify-center {item.is_checked
											? 'bg-green-500 border-green-500 text-white'
											: 'border-gray-300 hover:border-gray-400'}"
									>
										{#if item.is_checked}✓{/if}
									</button>
									<div class="flex-1 {item.is_checked ? 'text-gray-400 line-through' : ''}">
										<span class="font-medium">{item.name}</span>
										{#if item.quantity || item.unit}
											<span class="text-gray-500 ml-2">
												{item.quantity || ''} {item.unit || ''}
											</span>
										{/if}
										{#if item.added_manually}
											<span class="text-xs text-gray-400 ml-2">(manual)</span>
										{/if}
									</div>
									<button
										onclick={() => deleteItem(item)}
										class="opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-700 px-2"
									>
										×
									</button>
								</div>
							{/each}
						</div>
					</div>
				{/if}
			{/each}
		{/if}
	</div>
{/if}

{#if showAddModal}
	<div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
		<div class="bg-white p-6 rounded-lg shadow-xl max-w-md w-full mx-4">
			<h2 class="text-xl font-semibold mb-4">Add Item</h2>
			<form onsubmit={(e) => { e.preventDefault(); addItem(); }} class="space-y-4">
				{#if ingredients.length > 0}
					<div>
						<label for="ingredient" class="block text-sm font-medium text-gray-700 mb-1">
							Select Ingredient
						</label>
						<select
							id="ingredient"
							bind:value={selectedIngredientId}
							class="w-full px-4 py-2 border rounded-lg"
						>
							<option value={null}>-- Custom item --</option>
							{#each ingredients as ing}
								<option value={ing.id}>{ing.name}</option>
							{/each}
						</select>
					</div>
				{/if}

				{#if !selectedIngredientId}
					<div>
						<label for="itemName" class="block text-sm font-medium text-gray-700 mb-1">
							Item Name
						</label>
						<input
							id="itemName"
							type="text"
							bind:value={newItemName}
							class="w-full px-4 py-2 border rounded-lg"
						/>
					</div>
				{/if}

				<div class="grid grid-cols-2 gap-4">
					<div>
						<label for="itemQty" class="block text-sm font-medium text-gray-700 mb-1">
							Quantity
						</label>
						<input
							id="itemQty"
							type="text"
							bind:value={newItemQuantity}
							class="w-full px-4 py-2 border rounded-lg"
						/>
					</div>
					<div>
						<label for="itemUnit" class="block text-sm font-medium text-gray-700 mb-1">Unit</label>
						<input
							id="itemUnit"
							type="text"
							bind:value={newItemUnit}
							class="w-full px-4 py-2 border rounded-lg"
						/>
					</div>
				</div>

				<div class="flex gap-2">
					<button
						type="submit"
						class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
					>
						Add
					</button>
					<button
						type="button"
						onclick={() => (showAddModal = false)}
						class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
					>
						Cancel
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}
