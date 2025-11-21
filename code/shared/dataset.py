class Dataset:
    def __init__(self, headers, rows):
        self.headers = headers
        self.rows = rows

    def get_headers(self):
        return self.headers

    def get_rows(self):
        return self.rows

    def get_total_rows(self):
        return len(self.rows)
    
    def __str__(self):
        return f"Dataset{{rows={len(self.rows)}}}"
