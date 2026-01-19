import React, { useState, useEffect } from 'react'
import axios from 'axios'

function App() {
    const [articles, setArticles] = useState([])
    const [query, setQuery] = useState('')
    const [searchType, setSearchType] = useState('text')
    const [selectedTopic, setSelectedTopic] = useState(null)
    const [loading, setLoading] = useState(false)

    // Use relative URL so Vite proxy handles it
    const API_BASE = ''

    useEffect(() => {
        fetchArticles()
    }, [selectedTopic])

    const fetchArticles = async () => {
        setLoading(true)
        try {
            let url = `${API_BASE}/articles?limit=50`
            if (selectedTopic) {
                url = `${API_BASE}/topics/${selectedTopic}`
            }
            const res = await axios.get(url)
            setArticles(res.data)
        } catch (e) {
            console.error(e)
        }
        setLoading(false)
    }

    const handleSearch = async (e) => {
        e.preventDefault()
        if (!query) return fetchArticles()

        setLoading(true)
        try {
            const res = await axios.get(`${API_BASE}/search`, {
                params: { q: query, type: searchType }
            })
            setArticles(res.data)
            setSelectedTopic(null)
        } catch (e) {
            console.error(e)
        }
        setLoading(false)
    }

    const topics = ['Politics', 'Sports', 'Business', 'Technology', 'Education', 'Crime']

    return (
        <div className="container">
            <header>
                <h1>BCIIP Intelligence</h1>
                <p>Real-time internet intelligence platform for Bangladesh</p>
            </header>

            <form className="search-bar" onSubmit={handleSearch}>
                <input
                    type="text"
                    placeholder="Search articles..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                />
                <select value={searchType} onChange={(e) => setSearchType(e.target.value)}>
                    <option value="text">Keyword</option>
                    <option value="semantic">Semantic (AI)</option>
                </select>
                <button type="submit">Search</button>
            </form>

            <div className="filters">
                <span
                    className={`chip ${!selectedTopic ? 'active' : ''}`}
                    onClick={() => setSelectedTopic(null)}
                >
                    All
                </span>
                {topics.map(t => (
                    <span
                        key={t}
                        className={`chip ${selectedTopic === t ? 'active' : ''}`}
                        onClick={() => setSelectedTopic(t)}
                    >
                        {t}
                    </span>
                ))}
            </div>

            {loading && <p>Loading...</p>}

            <div className="article-list">
                {articles.map(article => (
                    <div key={article.id} className="article-card">
                        <h2>
                            <a href={article.url} target="_blank" rel="noopener noreferrer">
                                {article.title}
                            </a>
                        </h2>
                        <div className="meta">
                            <span>{article.source}</span> • <span>{new Date(article.published_at).toLocaleDateString()}</span>
                            {article.primary_category && ` • ${article.primary_category}`}
                        </div>
                        <p className="summary">
                            {article.summary_text || article.cleaned_text?.substring(0, 200) + '...'}
                        </p>

                        {article.entities && article.entities.length > 0 && (
                            <div className="entities">
                                {article.entities.slice(0, 5).map(ent => (
                                    <span key={ent.id} className="entity-tag">{ent.text}</span>
                                ))}
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    )
}

export default App
