import type { DietaryTag } from '$lib/types';

export const allDietaryTags: DietaryTag[] = [
	'vegetarian',
	'vegan',
	'gluten_free',
	'dairy_free',
	'nut_free',
	'low_carb',
	'keto',
	'paleo'
];

export const dietaryTagLabels: Record<DietaryTag, string> = {
	vegetarian: 'Vegetarian',
	vegan: 'Vegan',
	gluten_free: 'Gluten-Free',
	dairy_free: 'Dairy-Free',
	nut_free: 'Nut-Free',
	low_carb: 'Low-Carb',
	keto: 'Keto',
	paleo: 'Paleo'
};

export const dietaryTagColors: Record<DietaryTag, string> = {
	vegetarian: 'bg-green-100 text-green-800',
	vegan: 'bg-emerald-100 text-emerald-800',
	gluten_free: 'bg-amber-100 text-amber-800',
	dairy_free: 'bg-blue-100 text-blue-800',
	nut_free: 'bg-orange-100 text-orange-800',
	low_carb: 'bg-purple-100 text-purple-800',
	keto: 'bg-pink-100 text-pink-800',
	paleo: 'bg-teal-100 text-teal-800'
};
