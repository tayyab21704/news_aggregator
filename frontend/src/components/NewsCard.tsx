import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Clock, ExternalLink } from "lucide-react";

interface NewsArticle {
  id: string;
  title: string;
  summary: string;
  source: string;
  publishedAt: string;
  url: string;
  authors?: string[];
  mainText: string;
  imageUrl?: string;
  bias: 'left' | 'right' | 'center';
}

interface NewsCardProps {
  article: NewsArticle;
  onArticleClick: (article: NewsArticle) => void;
}

export const NewsCard = ({ article, onArticleClick }: NewsCardProps) => {
  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 60) {
      return `${diffInMinutes}m ago`;
    } else if (diffInMinutes < 1440) {
      return `${Math.floor(diffInMinutes / 60)}h ago`;
    } else {
      return `${Math.floor(diffInMinutes / 1440)}d ago`;
    }
  };

  return (
    <Card 
      className="group hover:shadow-lg transition-all duration-200 border-border hover:border-news-primary/20 bg-news-surface cursor-pointer"
      onClick={() => onArticleClick(article)}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <h3 className="font-semibold text-news-text-primary leading-tight line-clamp-2 group-hover:text-news-primary transition-colors">
            {article.title}
          </h3>
          <ExternalLink className="w-4 h-4 text-news-text-secondary flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>
        
        <div className="flex items-center gap-2 text-sm text-news-text-secondary">
          <span className="font-medium text-news-primary">{article.source}</span>
          <span>•</span>
          <div className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            <span>{formatTimeAgo(article.publishedAt)}</span>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        <p className="text-news-text-secondary line-clamp-3 leading-relaxed">
          {article.summary}
        </p>
      </CardContent>
    </Card>
  );
};