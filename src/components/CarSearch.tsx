
import React, { useState, useEffect } from 'react';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import { Loader2, Search, Car } from "lucide-react";
import { searchCars, CarListing } from "@/api/search";
import { isSupabaseConfigured } from "@/lib/supabase";

const CarSearch = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<CarListing[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [initialLoad, setInitialLoad] = useState(true);
  const { toast } = useToast();
  const [connectionStatus, setConnectionStatus] = useState<string>('');

  // Check Supabase connection on component mount
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const configured = isSupabaseConfigured();
        setConnectionStatus(configured ? 'Connected to Supabase' : 'Using mock data (Supabase not configured)');
        console.log('Supabase connection status:', configured);
      } catch (error) {
        console.error('Error checking Supabase connection:', error);
        setConnectionStatus('Error connecting to Supabase, using mock data');
      }
    };
    
    checkConnection();
  }, []);

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      toast({
        title: "Search query is empty",
        description: "Please enter a car brand or model to search",
        variant: "destructive"
      });
      return;
    }

    setIsLoading(true);
    setInitialLoad(false);

    try {
      console.log('Searching for:', searchQuery);
      // Use our API function with proper error handling
      const data = await searchCars(searchQuery);
      console.log('Search results:', data);
      setSearchResults(data);
      
      if (data.length === 0) {
        toast({
          title: "No results found",
          description: `No cars matching "${searchQuery}" were found`,
          variant: "default"
        });
      } else {
        toast({
          title: "Search complete",
          description: `Found ${data.length} results for "${searchQuery}"`,
          variant: "default"
        });
      }
    } catch (error) {
      console.error("Search error:", error);
      toast({
        title: "Search failed",
        description: "Failed to search for cars. Please try again later.",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      <div className="flex flex-col items-center mb-10">
        <div className="flex items-center mb-2">
          <Car className="h-8 w-8 mr-2 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">Finn Car Explorer</h1>
        </div>
        <p className="text-gray-500 text-center max-w-lg mb-6">
          Search through Finn.no's car database to find your next vehicle. Enter a brand or model to get started.
        </p>
        
        {connectionStatus && (
          <div className="text-sm mb-4 bg-blue-50 text-blue-700 px-3 py-1 rounded-full">
            {connectionStatus}
          </div>
        )}
      
        <div className="flex w-full max-w-lg gap-2">
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search for cars (e.g., Audi A3, Tesla)"
            className="flex-grow"
          />
          <Button onClick={handleSearch} disabled={isLoading} className="bg-blue-600 hover:bg-blue-700">
            {isLoading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Search className="h-4 w-4 mr-2" />}
            Search
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center items-center p-20">
          <Loader2 className="h-10 w-10 animate-spin text-blue-600" />
          <span className="ml-3 text-lg text-gray-600">Searching for cars...</span>
        </div>
      ) : (
        <>
          {!initialLoad && (
            <div className="mb-4">
              <h2 className="text-xl font-semibold text-gray-800">
                {searchResults.length > 0 
                  ? `Search results for "${searchQuery}" (${searchResults.length} found)` 
                  : `No results found for "${searchQuery}"`}
              </h2>
              <Separator className="mt-2" />
            </div>
          )}
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {searchResults.map((car) => (
              <Card key={car.finn_id} className="overflow-hidden hover:shadow-lg transition-shadow">
                <div className="h-48 overflow-hidden bg-gray-100">
                  {car.image_url ? (
                    <img 
                      src={car.image_url} 
                      alt={car.title} 
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center bg-gray-200">
                      <Car className="h-16 w-16 text-gray-400" />
                    </div>
                  )}
                </div>
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg">{car.title}</CardTitle>
                  <CardDescription>
                    {car.year} • {car.location}
                  </CardDescription>
                </CardHeader>
                <CardContent className="pb-2">
                  <div className="flex justify-between text-lg">
                    <span className="font-medium text-blue-600">{car.price}</span>
                    <span className="text-gray-600">ID: {car.finn_id}</span>
                  </div>
                </CardContent>
                <CardFooter>
                  <a 
                    href={car.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="w-full"
                  >
                    <Button variant="outline" className="w-full">
                      View on Finn.no
                    </Button>
                  </a>
                </CardFooter>
              </Card>
            ))}
          </div>

          {!initialLoad && searchResults.length === 0 && (
            <div className="text-center p-10">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
                <Search className="h-8 w-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-900">No cars found</h3>
              <p className="mt-1 text-gray-500">Try searching for a different brand or model</p>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default CarSearch;
