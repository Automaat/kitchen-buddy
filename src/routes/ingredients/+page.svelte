<script lang="ts">
	import type { Ingredient, IngredientCategory } from '$lib/types';
	import { api } from '$lib/utils';
	import { onMount } from 'svelte';

	let ingredients: Ingredient[] = $state([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let search = $state('');
	let showForm = $state(false);
	let editingId = $state<number | null>(null);

	let name = $state('');
	let category = $state<IngredientCategory>('other');
	let defaultUnit = $state('');

	const categories: IngredientCategory[] = [
		'produce',
		'dairy',
		'meat',
		'seafood',
		'pantry',
		'frozen',
		'bakery',
		'beverages',
		'condiments',
		'spices',
		'other'
	];

	async function loadIngredients() {
		loading = true;
		error = null;
		try {
			const params = new URLSearchParams();
			if (search) params.set('search', search);
			ingredients = await api.get<Ingredient[]>(`/ingredients?${params}`);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load ingredients';
		} finally {
			loading = false;
		}
	}

	onMount(loadIngredients);

	function resetForm() {
		name = '';
		category = 'other';
		defaultUnit = '';
		showForm = false;
		editingId = null;
	}

	function startEdit(ingredient: Ingredient) {
		name = ingredient.name;
		category = ingredient.category;
		defaultUnit = ingredient.default_unit || '';
		editingId = ingredient.id;
		showForm = true;
	}

	async function handleSubmit() {
		if (!name.trim()) return;

		try {
			const data = {
				name: name.trim(),
				category,
				default_unit: defaultUnit.trim() || null
			};

			if (editingId) {
				await api.put(`/ingredients/${editingId}`, data);
			} else {
				await api.post('/ingredients', data);
			}

			resetForm();
			await loadIngredients();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to save ingredient';
		}
	}

	async function deleteIngredient(id: number) {
		if (!confirm('Delete this ingredient?')) return;
		try {
			await api.delete(`/ingredients/${id}`);
			await loadIngredients();
		} catch {
			/* ignore */
		}
	}

	const categoryColors: Record<IngredientCategory, string> = {
		produce: 'bg-green-100 text-green-800',
		dairy: 'bg-blue-100 text-blue-800',
		meat: 'bg-red-100 text-red-800',
		seafood: 'bg-cyan-100 text-cyan-800',
		pantry: 'bg-amber-100 text-amber-800',
		frozen: 'bg-indigo-100 text-indigo-800',
		bakery: 'bg-orange-100 text-orange-800',
		beverages: 'bg-purple-100 text-purple-800',
		condiments: 'bg-yellow-100 text-yellow-800',
		spices: 'bg-rose-100 text-rose-800',
		other: 'bg-gray-100 text-gray-800'
	};
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h1 class="text-3xl font-bold text-gray-900">Ingredients</h1>
		<button
			onclick={() => {
				resetForm();
				showForm = true;
			}}
			class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
		>
			Add Ingredient
		</button>
	</div>

	{#if showForm}
		<div class="bg-white p-6 rounded-lg shadow-sm border">
			<h2 class="text-lg font-semibold mb-4">
				{editingId ? 'Edit Ingredient' : 'New Ingredient'}
			</h2>
			<form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-4">
				<div class="grid md:grid-cols-3 gap-4">
					<div>
						<label for="name" class="block text-sm font-medium text-gray-700 mb-1">Name *</label>
						<input
							id="name"
							type="text"
							bind:value={name}
							required
							class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
						/>
					</div>
					<div>
						<label for="category" class="block text-sm font-medium text-gray-700 mb-1">
							Category
						</label>
						<select id="category" bind:value={category} class="w-full px-4 py-2 border rounded-lg">
							{#each categories as cat}
								<option value={cat}>{cat}</option>
							{/each}
						</select>
					</div>
					<div>
						<label for="unit" class="block text-sm font-medium text-gray-700 mb-1">
							Default Unit
						</label>
						<input
							id="unit"
							type="text"
							bind:value={defaultUnit}
							placeholder="g, ml, pcs..."
							class="w-full px-4 py-2 border rounded-lg"
						/>
					</div>
				</div>
				<div class="flex gap-2">
					<button
						type="submit"
						class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
					>
						{editingId ? 'Update' : 'Add'}
					</button>
					<button
						type="button"
						onclick={resetForm}
						class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
					>
						Cancel
					</button>
				</div>
			</form>
		</div>
	{/if}

	<div class="bg-white p-4 rounded-lg shadow-sm border">
		<input
			type="text"
			placeholder="Search ingredients..."
			bind:value={search}
			oninput={loadIngredients}
			class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
		/>
	</div>

	{#if error}
		<div class="bg-red-50 text-red-700 p-4 rounded-lg">{error}</div>
	{/if}

	{#if loading}
		<div class="text-center py-12">Loading...</div>
	{:else if ingredients.length === 0}
		<div class="text-center py-12 text-gray-500">
			No ingredients found. Add some to get started!
		</div>
	{:else}
		<div class="bg-white rounded-lg shadow-sm border overflow-hidden">
			<table class="w-full">
				<thead class="bg-gray-50">
					<tr>
						<th class="px-4 py-3 text-left text-sm font-medium text-gray-700">Name</th>
						<th class="px-4 py-3 text-left text-sm font-medium text-gray-700">Category</th>
						<th class="px-4 py-3 text-left text-sm font-medium text-gray-700">Default Unit</th>
						<th class="px-4 py-3 text-right text-sm font-medium text-gray-700">Actions</th>
					</tr>
				</thead>
				<tbody class="divide-y">
					{#each ingredients as ingredient}
						<tr class="hover:bg-gray-50">
							<td class="px-4 py-3 font-medium">{ingredient.name}</td>
							<td class="px-4 py-3">
								<span
									class="px-2 py-0.5 rounded-full text-xs {categoryColors[ingredient.category]}"
								>
									{ingredient.category}
								</span>
							</td>
							<td class="px-4 py-3 text-gray-600">{ingredient.default_unit || '-'}</td>
							<td class="px-4 py-3 text-right">
								<button
									onclick={() => startEdit(ingredient)}
									class="text-blue-600 hover:underline mr-2"
								>
									Edit
								</button>
								<button
									onclick={() => deleteIngredient(ingredient.id)}
									class="text-red-600 hover:underline"
								>
									Delete
								</button>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>
