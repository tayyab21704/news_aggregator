import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Clock, ExternalLink, Volume2, Globe, FileText, BarChart3 } from "lucide-react";

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

interface ArticleModalProps {
  article: NewsArticle | null;
  isOpen: boolean;
  onClose: () => void;
}

export const ArticleModal = ({ article, isOpen, onClose }: ArticleModalProps) => {
  const [currentView, setCurrentView] = useState<'original' | 'summary' | 'translated'>('original');
  const [translatedText, setTranslatedText] = useState<string>("");
  const [summaryText, setSummaryText] = useState<string>("");

  if (!article) return null;

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getBiasColor = (bias: string) => {
    switch (bias) {
      case 'left': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'right': return 'bg-red-100 text-red-800 border-red-200';
      case 'center': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getCurrentText = () => {
    switch (currentView) {
      case 'summary': return summaryText || "Summary will be generated...";
      case 'translated': return translatedText || "Translation will be generated...";
      default: return article.mainText;
    }
  };

  const handleSummary = () => {
    setCurrentView('summary');
    if (!summaryText) {
      setSummaryText("This is a generated summary of the article. The main points include the key findings and conclusions...");
    }
  };

  const handleTranslate = () => {
    setCurrentView('translated');
    if (!translatedText) {
      setTranslatedText("Esta es una traducción del artículo. El contenido principal incluye...");
    }
  };

  const handleListen = () => {
    // Placeholder for podcast/audio functionality
    console.log("Starting audio playback...");
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh] p-0 overflow-hidden">
        <div className="flex h-full">
          {/* Main Content */}
          <div className="flex-1 flex flex-col">
            <DialogHeader className="px-6 py-4 border-b">
              <DialogTitle className="text-xl font-bold text-news-text-primary pr-8">
                {article.title}
              </DialogTitle>
              
              <div className="flex items-center gap-4 text-sm text-news-text-secondary mt-2">
                <span className="font-medium text-news-primary">{article.source}</span>
                <div className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  <span>{formatDate(article.publishedAt)}</span>
                </div>
                {article.authors && article.authors.length > 0 && (
                  <span>By {article.authors.join(', ')}</span>
                )}
                <a 
                  href={article.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 text-news-primary hover:underline"
                >
                  <ExternalLink className="w-3 h-3" />
                  Original
                </a>
              </div>
            </DialogHeader>

            <div className="flex-1 overflow-y-auto px-6 py-4">
              {article.imageUrl && (
                <img 
                  src={article.imageUrl} 
                  alt="Article" 
                  className="w-full max-w-2xl mx-auto mb-6 rounded-lg"
                />
              )}
              
              <div className="prose prose-lg max-w-none text-news-text-primary">
                <p className="whitespace-pre-wrap leading-relaxed">
                  {getCurrentText()}
                </p>
              </div>
            </div>
          </div>

          {/* Right Sidebar */}
          <div className="w-80 bg-news-surface border-l border-border p-6 flex flex-col gap-4">
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-news-text-primary mb-2 flex items-center gap-2">
                  <BarChart3 className="w-4 h-4" />
                  Bias Analysis
                </h3>
                <Badge className={`capitalize ${getBiasColor(article.bias)}`}>
                  {article.bias} leaning
                </Badge>
              </div>

              <div className="space-y-2">
                <h3 className="font-semibold text-news-text-primary mb-3">Article Tools</h3>
                
                <Button 
                  variant={currentView === 'summary' ? 'default' : 'outline'} 
                  className="w-full justify-start"
                  onClick={handleSummary}
                >
                  <FileText className="w-4 h-4 mr-2" />
                  Summary
                </Button>
                
                <Button 
                  variant={currentView === 'translated' ? 'default' : 'outline'} 
                  className="w-full justify-start"
                  onClick={handleTranslate}
                >
                  <Globe className="w-4 h-4 mr-2" />
                  Translate
                </Button>
                
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={handleListen}
                >
                  <Volume2 className="w-4 h-4 mr-2" />
                  Listen as Podcast
                </Button>

                <Button 
                  variant={currentView === 'original' ? 'default' : 'outline'} 
                  className="w-full justify-start"
                  onClick={() => setCurrentView('original')}
                >
                  Original Text
                </Button>
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};