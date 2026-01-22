<script lang="ts">
	import '../app.css';

	const navItems = [
		{ href: '/', label: 'Dashboard', icon: '🏠' },
		{ href: '/recipes', label: 'Recipes', icon: '📖' },
		{ href: '/collections', label: 'Collections', icon: '📚' },
		{ href: '/meal-planner', label: 'Meal Planner', icon: '📅' },
		{ href: '/shopping-lists', label: 'Shopping Lists', icon: '🛒' },
		{ href: '/pantry', label: 'Pantry', icon: '🗄️' },
		{ href: '/suggestions', label: 'Suggestions', icon: '💡' },
		{ href: '/ingredients', label: 'Ingredients', icon: '🥕' },
		{ href: '/favorites', label: 'Favorites', icon: '⭐' }
	];

	let { children } = $props();
</script>

<div class="min-h-screen bg-gray-50">
	<nav class="bg-white shadow-sm border-b">
		<div class="max-w-7xl mx-auto px-4">
			<div class="flex items-center justify-between h-16">
				<a href="/" class="text-xl font-bold text-gray-900">Kitchen Buddy</a>
				<div class="flex space-x-4">
					{#each navItems as item}
						<a
							href={item.href}
							class="px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100"
						>
							<span class="mr-1">{item.icon}</span>
							{item.label}
						</a>
					{/each}
				</div>
			</div>
		</div>
	</nav>

	<main class="max-w-7xl mx-auto px-4 py-8">
		{@render children()}
	</main>
</div>
