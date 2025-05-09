
import { supabase } from '@/lib/supabase';

export interface CarListing {
  finn_id: string;
  title: string;
  brand: string;
  model: string;
  year: string;
  price: string;
  location: string;
  url: string;
  image_url: string | null;
}

/**
 * Search for cars in the Supabase database
 */
export const searchCars = async (query: string): Promise<CarListing[]> => {
  try {
    // If Supabase is properly connected and has data
    if (supabase) {
      const sanitizedQuery = query.toLowerCase().trim();
      
      const { data, error } = await supabase
        .from('cars')
        .select('*')
        .or(`brand.ilike.%${sanitizedQuery}%,model.ilike.%${sanitizedQuery}%,title.ilike.%${sanitizedQuery}%`)
        .limit(20);
      
      if (error) {
        console.error('Supabase search error:', error);
        throw error;
      }
      
      return data as CarListing[];
    }
    
    // Fallback to mock data if Supabase isn't available
    console.log('Supabase not configured, using mock data');
    return getMockData(query);
  } catch (error) {
    console.error('Search error:', error);
    return getMockData(query);
  }
};

/**
 * Get mock car data for demonstration
 */
const getMockData = (query: string): CarListing[] => {
  const mockData: CarListing[] = [
    {
      finn_id: "406967386",
      title: "Audi A3 Sportback e-tron",
      brand: "Audi",
      model: "A3",
      year: "2018",
      price: "289,000 kr",
      location: "Oslo",
      url: "https://www.finn.no/mobility/item/406967386",
      image_url: "https://images.finncdn.no/dynamic/1600w/2023/11/vertical-0/26/4/267/354/47_1395823842.jpg"
    },
    {
      finn_id: "406915143",
      title: "Audi A3 Sportback TFSI e",
      brand: "Audi",
      model: "A3",
      year: "2022",
      price: "399,000 kr",
      location: "Bergen",
      url: "https://www.finn.no/mobility/item/406915143",
      image_url: "https://images.finncdn.no/dynamic/1600w/2023/11/vertical-0/25/0/265/081/85_1208593260.jpg"
    }
  ];
  
  // Filter mock data based on query
  if (!query) return mockData;
  
  const lowercaseQuery = query.toLowerCase();
  return mockData.filter(car => 
    car.brand.toLowerCase().includes(lowercaseQuery) || 
    car.model.toLowerCase().includes(lowercaseQuery) || 
    car.title.toLowerCase().includes(lowercaseQuery)
  );
};
