import { Newspaper, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface NewsHeaderProps {
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

export const NewsHeader = ({ onRefresh, isRefreshing = false }: NewsHeaderProps) => {
  return (
    <header className="bg-news-surface border-b border-border shadow-sm">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-news-primary to-news-secondary rounded-lg">
              <Newspaper className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-news-text-primary">
                NewsFlow
              </h1>
              <p className="text-news-text-secondary text-sm">
                Stay informed with the latest news
              </p>
            </div>
          </div>
          
          {onRefresh && (
            <Button
              onClick={onRefresh}
              variant="outline"
              size="sm"
              disabled={isRefreshing}
              className="flex items-center gap-2 border-news-primary/20 text-news-primary hover:bg-news-accent"
            >
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          )}
        </div>
      </div>
    </header>
  );
};