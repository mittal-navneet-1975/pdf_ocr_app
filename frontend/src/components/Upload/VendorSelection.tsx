import React, { useState } from 'react';
import { Building, ArrowLeft, Search } from 'lucide-react';
import { Vendor } from '../../types';

interface VendorSelectionProps {
  productId: string;
  selectedVendor: string;
  onVendorSelect: (vendorId: string) => void;
  onBack: () => void;
}

const mockVendors: Vendor[] = [
  { id: '1', name: 'CalproSpecialities Pvt. Ltd.', productIds: ['1'] },
  { id: '2', name: 'Mahaan Milk Food Limited', productIds: ['1'] },
  { id: '3', name: 'Optilec - Kriti', productIds: ['2'] },
  { id: '4', name: 'ADM Agro Industries India Private Limited', productIds: ['2'] }
];

export function VendorSelection({ productId, selectedVendor, onVendorSelect, onBack }: VendorSelectionProps) {
  const [search, setSearch] = useState("");

  const filteredVendors = mockVendors.filter(vendor =>
    vendor.productIds.includes(productId) &&
    vendor.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <div className="flex items-center mb-6">
        <button
          onClick={onBack}
          className="mr-4 p-2 rounded-lg border border-gray-300 hover:bg-gray-50"
        >
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Select Vendor</h2>
          <p className="text-gray-600">Choose the vendor for this product category</p>
        </div>
      </div>

      {/* Search bar */}
      <div className="flex items-center mb-4 border rounded-lg p-2 bg-white">
        <Search className="h-5 w-5 text-gray-500 mr-2" />
        <input
          type="text"
          placeholder="Search vendor..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full outline-none"
        />
      </div>

      <div className="space-y-2">
        {filteredVendors.map((vendor) => (
          <button
            key={vendor.id}
            onClick={() => onVendorSelect(vendor.id)}
            className={`w-full p-4 rounded-lg border-2 text-left transition-all duration-200 hover:scale-105 ${
              selectedVendor === vendor.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center">
              <Building className="h-6 w-6 text-blue-600 mr-3" />
              <h3 className="font-semibold text-gray-900">{vendor.name}</h3>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
