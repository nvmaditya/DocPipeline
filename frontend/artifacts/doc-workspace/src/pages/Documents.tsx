import { Layout } from "@/components/Layout";
import { FileUploader } from "@/components/FileUploader";
import { useListDocuments, useDeleteDocument, getListDocumentsQueryKey } from "@workspace/api-client-react";
import { useQueryClient } from "@tanstack/react-query";
import { FileText, Trash2, Loader2, AlertCircle } from "lucide-react";
import { formatBytes } from "@/lib/utils";
import { format } from "date-fns";
import { motion } from "framer-motion";
import { useToast } from "@/hooks/use-toast";

export default function Documents() {
  const { data, isLoading, error } = useListDocuments();
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const { mutate: deleteDoc, isPending: isDeleting } = useDeleteDocument({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: getListDocumentsQueryKey() });
        toast({ title: "Document deleted" });
      },
      onError: () => {
        toast({ variant: "destructive", title: "Failed to delete document" });
      }
    }
  });

  const documents = data?.documents || [];

  return (
    <Layout>
      <div className="flex-1 overflow-y-auto p-6 md:p-12 space-y-12">
        
        {/* Header & Uploader */}
        <section>
          <div className="mb-8">
            <h1 className="text-3xl font-display font-bold text-foreground">Document Library</h1>
            <p className="text-muted-foreground mt-2">Manage your uploaded files and monitor processing status.</p>
          </div>
          
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <FileUploader />
          </motion.div>
        </section>

        {/* Document List */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-display font-bold">Your Files</h2>
            <span className="bg-primary/10 text-primary font-semibold px-3 py-1 rounded-full text-sm">
              {data?.total || 0} Files
            </span>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-20 text-muted-foreground">
              <Loader2 className="w-8 h-8 animate-spin" />
            </div>
          ) : error ? (
            <div className="bg-muted/20 border border-border/50 text-muted-foreground rounded-xl p-6 flex items-center gap-4">
              <AlertCircle className="w-6 h-6" />
              <div>
                <h4 className="font-bold text-foreground">Login required</h4>
                <p className="text-sm opacity-90">Login to see your library.</p>
              </div>
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-20 bg-card border border-border border-dashed rounded-2xl">
              <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
                <FileText className="w-8 h-8 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Your library is empty</h3>
              <p className="text-muted-foreground max-w-md mx-auto">
                Upload your first document above. We support PDF, Word, plain text, and more.
              </p>
            </div>
          ) : (
            <div className="bg-card border border-border rounded-2xl overflow-hidden shadow-lg shadow-black/5">
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b border-border/50 bg-muted/20">
                      <th className="px-6 py-4 font-semibold text-sm text-muted-foreground">Name</th>
                      <th className="px-6 py-4 font-semibold text-sm text-muted-foreground">Size</th>
                      <th className="px-6 py-4 font-semibold text-sm text-muted-foreground">Status</th>
                      <th className="px-6 py-4 font-semibold text-sm text-muted-foreground">Uploaded</th>
                      <th className="px-6 py-4 font-semibold text-sm text-muted-foreground text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/50">
                    {documents.map((doc) => (
                      <tr key={doc.id} className="hover:bg-white/5 transition-colors group">
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-lg bg-blue-500/10 text-blue-500 flex items-center justify-center shrink-0">
                              <FileText className="w-5 h-5" />
                            </div>
                            <div>
                              <p className="font-medium text-foreground max-w-[200px] sm:max-w-xs md:max-w-md truncate">
                                {doc.name}
                              </p>
                              <p className="text-xs text-muted-foreground uppercase mt-0.5">{doc.fileType}</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-muted-foreground whitespace-nowrap">
                          {formatBytes(doc.fileSize)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold uppercase tracking-wider
                            ${doc.status === 'ready' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 
                              doc.status === 'processing' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : 
                              doc.status === 'error' ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 
                              'bg-blue-500/10 text-blue-400 border border-blue-500/20'}`}
                          >
                            {doc.status === 'processing' && <Loader2 className="w-3 h-3 mr-1.5 animate-spin" />}
                            {doc.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-muted-foreground whitespace-nowrap">
                          {format(new Date(doc.createdAt), 'MMM d, yyyy')}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <button
                            onClick={() => deleteDoc({ documentId: doc.id })}
                            disabled={isDeleting}
                            className="p-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-lg transition-colors opacity-0 group-hover:opacity-100 focus:opacity-100 disabled:opacity-50"
                            title="Delete document"
                          >
                            <Trash2 className="w-5 h-5" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </section>
      </div>
    </Layout>
  );
}
