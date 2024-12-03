# Best Practices

1. Use context managers for cleanup:
```python
with BiocFileCache("cache_directory") as cache:
    cache.add("myfile", "path/to/file.txt")
```

2. Add tags for better organization:
```python
cache.add("data.csv", "data.csv", tags=["raw", "csv", "2024"])
```

3. Set expiration dates for temporary files:
```python
cache.add("temp.txt", "temp.txt", expires=datetime.now() + timedelta(hours=1))
```

4. Regular maintenance:
```python
# Periodically clean up expired resources
cache.cleanup()

# Monitor cache size
stats = cache.get_stats()
if stats["cache_size_bytes"] > threshold:
    # Take action
```