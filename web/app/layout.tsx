export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <title>RAG Assistant</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body style={{ fontFamily: 'system-ui, sans-serif', margin: 0, padding: 20, background: '#111', color: '#eee' }}>
        <main style={{ maxWidth: 800, margin: '0 auto' }}>{children}</main>
      </body>
    </html>
  );
}

