from langchain_text_splitters import RecursiveCharacterTextSplitter

class CodeSplitter:
    def __init__(self):
        """
        Initialize splitter with optimal settings
        """
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,      # max characters per chunk
            chunk_overlap=100    # overlap between chunks
        )

    def split_documents(self, parsed_data):
        """
        Convert parsed files into chunks
        """
        chunks = []

        for item in parsed_data:
            file_path = item["file"]
            content = item["content"]

            # Split text into chunks
            split_texts = self.splitter.split_text(content)

            for chunk in split_texts:
                chunks.append({
                    "content": chunk,
                    "metadata": {
                        "file": file_path
                    }
                })

        return chunks