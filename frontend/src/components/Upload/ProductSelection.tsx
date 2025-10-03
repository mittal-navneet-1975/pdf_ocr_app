import React, { useState } from 'react';
import { Package, Search } from 'lucide-react';
import { Product } from '../../types';

interface ProductSelectionProps {
  selectedProduct: string;
  onProductSelect: (productId: string) => void;
}

const mockProducts: Product[] = [
  { id: '1', name: 'Whey Permeate Powder' },
  { id: '2', name: 'Non GMO Soya Lecithin' }
];

export function ProductSelection({ selectedProduct, onProductSelect }: ProductSelectionProps) {
  const [search, setSearch] = useState("");

  const filteredProducts = mockProducts.filter(product =>
    product.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <div className="text-center mb-6">
        <Package className="mx-auto h-12 w-12 text-blue-600 mb-4" />
        <h2 className="text-2xl font-bold text-gray-900">Select Product Category</h2>
        <p className="text-gray-600 mt-2">Choose the product category for compliance review</p>
      </div>

      {/* Search bar */}
      <div className="flex items-center mb-4 border rounded-lg p-2 bg-white">
        <Search className="h-5 w-5 text-gray-500 mr-2" />
        <input
          type="text"
          placeholder="Search product..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full outline-none"
        />
      </div>

      <div className="space-y-2">
        {filteredProducts.map((product) => (
          <button
            key={product.id}
            onClick={() => onProductSelect(product.id)}
            className={`w-full p-4 rounded-lg border-2 text-left transition-all duration-200 hover:scale-105 ${
              selectedProduct === product.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center">
              <Package className="h-6 w-6 text-blue-600 mr-2" />
              <div>
                <h3 className="font-semibold text-gray-900">{product.name}</h3>
                <p className="text-sm text-gray-600">{product.category}</p>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
