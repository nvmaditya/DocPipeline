import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { useUploadDocument, getListDocumentsQueryKey } from "@workspace/api-client-react";
import { useQueryClient } from "@tanstack/react-query";
import { UploadCloud, File as FileIcon, X, Loader2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";

interface FileUploaderProps {
  onUploadSuccess?: () => void;
}

export function FileUploader({ onUploadSuccess }: FileUploaderProps) {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const { mutate: upload, isPending } = useUploadDocument({
    mutation: {
      onSuccess: () => {
        toast({
          title: "Upload complete",
          description: "Your document is now being processed for semantic search.",
        });
        setSelectedFile(null);
        queryClient.invalidateQueries({ queryKey: getListDocumentsQueryKey() });
        if (onUploadSuccess) onUploadSuccess();
      },
      onError: (err: any) => {
        toast({
          variant: "destructive",
          title: "Upload failed",
          description: err?.message || "There was an error uploading your document.",
        });
      }
    }
  });

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    maxFiles: 1,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
    }
  });

  const handleUpload = () => {
    if (selectedFile) {
      upload({ data: { file: selectedFile } });
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      {!selectedFile ? (
        <div
          {...getRootProps()}
          className={cn(
            "border-2 border-dashed rounded-3xl p-10 text-center cursor-pointer transition-all duration-300 group",
            isDragActive 
              ? "border-primary bg-primary/5 glow-primary" 
              : "border-border/60 hover:border-primary/50 hover:bg-white/5"
          )}
        >
          <input {...getInputProps()} />
          <div className="w-16 h-16 rounded-full bg-primary/10 text-primary flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
            <UploadCloud className="w-8 h-8" />
          </div>
          <h3 className="text-xl font-display font-semibold mb-2">
            {isDragActive ? "Drop your document here" : "Click or drag to upload"}
          </h3>
          <p className="text-muted-foreground text-sm max-w-sm mx-auto">
            Supports PDF, DOCX, TXT, MD, CSV, XLSX, PPTX. Your file will be processed and indexed for semantic search.
          </p>
        </div>
      ) : (
        <div className="bg-card border border-border rounded-2xl p-6 shadow-xl shadow-black/20">
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-blue-500/20 text-blue-400 flex items-center justify-center">
                <FileIcon className="w-6 h-6" />
              </div>
              <div>
                <h4 className="font-semibold text-foreground truncate max-w-[200px] md:max-w-md">
                  {selectedFile.name}
                </h4>
                <p className="text-sm text-muted-foreground">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            <button 
              onClick={() => setSelectedFile(null)}
              disabled={isPending}
              className="p-2 hover:bg-white/10 rounded-full text-muted-foreground hover:text-foreground transition-colors disabled:opacity-50"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <button
            onClick={handleUpload}
            disabled={isPending}
            className="w-full py-4 rounded-xl font-semibold bg-primary text-primary-foreground shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/40 hover:-translate-y-0.5 active:translate-y-0 transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:pointer-events-none"
          >
            {isPending ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Processing Document...
              </>
            ) : (
              <>
                <UploadCloud className="w-5 h-5" />
                Upload and Process
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
}
