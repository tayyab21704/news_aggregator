import { useState, useEffect } from "react";
import { NewsHeader } from "@/components/NewsHeader";
import { SearchBar } from "@/components/SearchBar";
import { NewsCard } from "@/components/NewsCard";
import { LoadingSkeleton } from "@/components/LoadingSkeleton";
import { ArticleModal } from "@/components/ArticleModal";
import { useToast } from "@/hooks/use-toast";

// Mock data for demonstration - replace with your FastAPI calls
const mockArticles = [
  {
    id: "1",
    title: "Revolutionary AI Technology Transforms Healthcare Industry",
    summary: "A groundbreaking artificial intelligence system is showing remarkable results in early disease detection, potentially saving thousands of lives through faster and more accurate diagnoses.",
    source: "TechNews",
    publishedAt: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
    url: "https://example.com/ai-healthcare",
    authors: ["Dr. Sarah Johnson", "Michael Chen"],
    mainText: "The healthcare industry is experiencing a revolutionary transformation with the introduction of advanced artificial intelligence systems that are demonstrating unprecedented accuracy in early disease detection. This groundbreaking technology utilizes machine learning algorithms trained on millions of medical images and patient records to identify potential health issues before they become critical.\n\nThe AI system, developed by a team of researchers at leading medical institutions, has shown remarkable results in clinical trials. In a recent study involving over 10,000 patients, the AI successfully identified early-stage cancers with 95% accuracy, significantly outperforming traditional diagnostic methods.\n\nDr. Sarah Johnson, lead researcher on the project, explains that the system works by analyzing patterns in medical data that are often too subtle for human detection. 'We're not replacing doctors,' she emphasizes, 'but rather providing them with a powerful tool that can help save lives through earlier intervention.'\n\nThe implications of this technology extend far beyond cancer detection. The AI system has also demonstrated effectiveness in identifying cardiovascular diseases, neurological conditions, and rare genetic disorders. Healthcare providers are optimistic that this technology could significantly reduce healthcare costs while improving patient outcomes.\n\nImplementation of the AI system is already underway in several major hospitals across the country, with plans for wider deployment in the coming year.",
    imageUrl: "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800&h=400&fit=crop",
    bias: "center" as const
  },
  {
    id: "2", 
    title: "Global Climate Summit Reaches Historic Agreement",
    summary: "World leaders unite on ambitious climate targets, pledging unprecedented investment in renewable energy and carbon reduction technologies.",
    source: "Environmental Today",
    publishedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    url: "https://example.com/climate-summit",
    authors: ["Emma Rodriguez"],
    mainText: "In a landmark moment for global environmental policy, world leaders have reached a historic agreement at the International Climate Summit, committing to the most ambitious climate targets ever established. The agreement, signed by representatives from 195 countries, outlines a comprehensive roadmap for achieving net-zero carbon emissions by 2050.\n\nThe summit, held over five intensive days of negotiations, saw unprecedented cooperation between nations that have historically disagreed on climate policy. The final agreement includes specific commitments for renewable energy investment, carbon pricing mechanisms, and technology sharing initiatives.\n\nKey provisions of the agreement include a commitment to triple renewable energy capacity by 2030, establish a global carbon tax framework, and create a $100 billion annual fund to support developing nations in their transition to clean energy. Additionally, participating countries agreed to phase out coal-fired power plants by 2035.\n\nEnvironmental advocates are cautiously optimistic about the agreement, noting that its success will depend heavily on implementation and enforcement mechanisms. Critics, however, argue that the targets may still be insufficient to prevent the most catastrophic effects of climate change.\n\nThe agreement will now need to be ratified by individual national governments, a process that could take several years to complete.",
    imageUrl: "https://images.unsplash.com/photo-1611273426858-450d8e3c9fce?w=800&h=400&fit=crop",
    bias: "left" as const
  },
  {
    id: "3",
    title: "Space Exploration Milestone: New Discoveries on Mars",
    summary: "Latest rover mission uncovers evidence of ancient water systems, bringing scientists closer to understanding the possibility of past life on the red planet.",
    source: "Space Journal",
    publishedAt: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
    url: "https://example.com/mars-discovery",
    authors: ["Dr. James Wright", "Dr. Lisa Park"],
    mainText: "NASA's latest Mars rover mission has achieved a groundbreaking discovery that could reshape our understanding of the Red Planet's history and potential for past life. The rover has uncovered compelling evidence of extensive ancient water systems, including what appears to be remnants of river deltas and lake beds that existed billions of years ago.\n\nThe discovery was made possible through advanced geological analysis tools aboard the rover, which detected mineral compositions consistent with long-term water exposure. Sedimentary rock formations found in the Jezero Crater show clear signs of having been shaped by flowing water over extended periods.\n\n'This is the most significant evidence we've found for sustained water activity on Mars,' said Dr. James Wright, mission lead scientist. 'These formations suggest that Mars had a much more Earth-like environment in its distant past than we previously understood.'\n\nThe implications extend far beyond geological curiosity. The presence of ancient water systems dramatically increases the likelihood that microbial life could have existed on Mars. The rover has collected several samples that will be returned to Earth in a future mission for detailed biological analysis.\n\nThis discovery comes at a time when multiple space agencies are planning crewed missions to Mars within the next two decades. Understanding the planet's water history will be crucial for these missions, both for scientific research and potential resource utilization.",
    bias: "center" as const
  }
];

const Index = () => {
  const [articles, setArticles] = useState<typeof mockArticles>([]);
  const [filteredArticles, setFilteredArticles] = useState<typeof mockArticles>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedArticle, setSelectedArticle] = useState<typeof mockArticles[0] | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { toast } = useToast();

  // Simulate API call - replace with your FastAPI endpoint
  const fetchArticles = async () => {
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Replace this with: const response = await fetch('your-fastapi-endpoint/articles');
      // const data = await response.json();
      
      setArticles(mockArticles);
      setFilteredArticles(mockArticles);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch news articles",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  const handleSearch = (query: string) => {
    if (!query.trim()) {
      setFilteredArticles(articles);
      return;
    }

    const filtered = articles.filter(article =>
      article.title.toLowerCase().includes(query.toLowerCase()) ||
      article.summary.toLowerCase().includes(query.toLowerCase()) ||
      article.source.toLowerCase().includes(query.toLowerCase())
    );

    setFilteredArticles(filtered);
    
    if (filtered.length === 0) {
      toast({
        title: "No results found",
        description: `No articles match "${query}"`,
      });
    }
  };

  const handleRefresh = () => {
    setIsRefreshing(true);
    fetchArticles();
  };

  const handleArticleClick = (article: typeof mockArticles[0]) => {
    setSelectedArticle(article);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedArticle(null);
  };

  useEffect(() => {
    fetchArticles();
  }, []);

  return (
    <div className="min-h-screen bg-background">
      <NewsHeader onRefresh={handleRefresh} isRefreshing={isRefreshing} />
      
      <main className="container mx-auto px-4 py-8">
        <div className="space-y-8">
          <SearchBar onSearch={handleSearch} />
          
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-semibold text-news-text-primary">
                Latest News
              </h2>
              <span className="text-news-text-secondary text-sm">
                {filteredArticles.length} articles
              </span>
            </div>
            
            {isLoading ? (
              <LoadingSkeleton />
            ) : (
              <div className="grid gap-4 md:gap-6">
                {filteredArticles.map((article) => (
                  <NewsCard 
                    key={article.id} 
                    article={article} 
                    onArticleClick={handleArticleClick}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </main>

      <ArticleModal 
        article={selectedArticle}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
      />
    </div>
  );
};

export default Index;
