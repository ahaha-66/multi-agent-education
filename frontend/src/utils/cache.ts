interface CacheItem<T> {
  value: T;
  timestamp: number;
  expiresAt: number;
}

class Cache {
  private cache: Map<string, CacheItem<any>>;
  private defaultTTL: number;

  constructor(defaultTTL: number = 5 * 60 * 1000) {
    this.cache = new Map();
    this.defaultTTL = defaultTTL;
    
    if (typeof window !== 'undefined') {
      setInterval(() => this.cleanup(), 60000);
    }
  }

  set<T>(key: string, value: T, ttl?: number): void {
    const now = Date.now();
    const expiresAt = now + (ttl || this.defaultTTL);
    
    this.cache.set(key, {
      value,
      timestamp: now,
      expiresAt,
    });

    if (typeof window !== 'undefined') {
      try {
        const cacheData = JSON.stringify({
          value,
          timestamp: now,
          expiresAt,
        });
        localStorage.setItem(`cache_${key}`, cacheData);
      } catch (error) {
        console.warn('Failed to save to localStorage:', error);
      }
    }
  }

  get<T>(key: string): T | null {
    const item = this.cache.get(key);
    
    if (!item) {
      if (typeof window !== 'undefined') {
        try {
          const stored = localStorage.getItem(`cache_${key}`);
          if (stored) {
            const parsed = JSON.parse(stored) as CacheItem<T>;
            if (parsed.expiresAt > Date.now()) {
              this.cache.set(key, parsed);
              return parsed.value;
            } else {
              localStorage.removeItem(`cache_${key}`);
            }
          }
        } catch (error) {
          console.warn('Failed to read from localStorage:', error);
        }
      }
      return null;
    }

    if (item.expiresAt < Date.now()) {
      this.cache.delete(key);
      if (typeof window !== 'undefined') {
        localStorage.removeItem(`cache_${key}`);
      }
      return null;
    }

    return item.value as T;
  }

  has(key: string): boolean {
    return this.get(key) !== null;
  }

  delete(key: string): void {
    this.cache.delete(key);
    if (typeof window !== 'undefined') {
      localStorage.removeItem(`cache_${key}`);
    }
  }

  clear(): void {
    this.cache.clear();
    if (typeof window !== 'undefined') {
      const keysToRemove: string[] = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key?.startsWith('cache_')) {
          keysToRemove.push(key);
        }
      }
      keysToRemove.forEach(key => localStorage.removeItem(key));
    }
  }

  private cleanup(): void {
    const now = Date.now();
    const keysToDelete: string[] = [];

    this.cache.forEach((item, key) => {
      if (item.expiresAt < now) {
        keysToDelete.push(key);
      }
    });

    keysToDelete.forEach(key => this.delete(key));
  }

  size(): number {
    return this.cache.size;
  }

  keys(): string[] {
    return Array.from(this.cache.keys());
  }
}

export const cache = new Cache();

export function memoize<T extends (...args: any[]) => any>(
  fn: T,
  keyGenerator?: (...args: Parameters<T>) => string,
  ttl?: number
): T {
  return ((...args: Parameters<T>) => {
    const key = keyGenerator 
      ? keyGenerator(...args) 
      : JSON.stringify(args);
    
    const cached = cache.get(key);
    if (cached !== null) {
      return cached as ReturnType<T>;
    }

    const result = fn(...args);
    
    if (result instanceof Promise) {
      return result.then((resolved) => {
        cache.set(key, resolved, ttl);
        return resolved;
      }) as ReturnType<T>;
    }

    cache.set(key, result, ttl);
    return result;
  }) as T;
}
