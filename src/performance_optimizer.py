"""
Performance Optimization System
"""
import streamlit as st
import time
import psutil
import gc
from functools import wraps
from typing import Any, Callable
import threading
import asyncio

class PerformanceOptimizer:
    def __init__(self):
        self.cache_stats = {'hits': 0, 'misses': 0}
        self.performance_metrics = {}
    
    @staticmethod
    def monitor_performance(func: Callable) -> Callable:
        """Decorator to monitor function performance"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            try:
                result = func(*args, **kwargs)
                success = True
            except Exception as e:
                result = None
                success = False
                raise e
            finally:
                end_time = time.time()
                end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                
                # Store performance metrics
                if not hasattr(st.session_state, 'performance_metrics'):
                    st.session_state.performance_metrics = {}
                
                st.session_state.performance_metrics[func.__name__] = {
                    'execution_time': end_time - start_time,
                    'memory_used': end_memory - start_memory,
                    'success': success,
                    'timestamp': time.time()
                }
            
            return result
        return wrapper
    
    @staticmethod
    def optimize_memory():
        """Optimize memory usage"""
        # Force garbage collection
        gc.collect()
        
        # Clear matplotlib cache
        try:
            import matplotlib.pyplot as plt
            plt.close('all')
        except:
            pass
        
        # Clear plotly cache
        try:
            import plotly.io as pio
            pio.kaleido.scope._shutdown_kaleido()
        except:
            pass
    
    @staticmethod
    def async_processing(func: Callable):
        """Decorator for async processing"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            def run_async():
                return func(*args, **kwargs)
            
            # Run in thread for CPU-bound tasks
            thread = threading.Thread(target=run_async)
            thread.start()
            
            # Show progress while processing
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            progress = 0
            while thread.is_alive():
                progress = min(progress + 0.1, 0.9)
                progress_bar.progress(progress)
                status_text.text(f"Processing... {progress*100:.0f}%")
                time.sleep(0.1)
            
            thread.join()
            progress_bar.progress(1.0)
            status_text.text("Complete!")
            
            # Clean up
            progress_bar.empty()
            status_text.empty()
            
            return run_async()
        
        return wrapper
    
    @staticmethod
    def cache_large_computations(ttl: int = 300):
        """Cache large computations with TTL"""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Create cache key
                cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
                
                # Check cache
                if hasattr(st.session_state, 'computation_cache'):
                    cache_entry = st.session_state.computation_cache.get(cache_key)
                    if cache_entry and (time.time() - cache_entry['timestamp']) < ttl:
                        return cache_entry['result']
                
                # Compute and cache
                result = func(*args, **kwargs)
                
                if not hasattr(st.session_state, 'computation_cache'):
                    st.session_state.computation_cache = {}
                
                st.session_state.computation_cache[cache_key] = {
                    'result': result,
                    'timestamp': time.time()
                }
                
                return result
            
            return wrapper
        return decorator
    
    @staticmethod
    def display_performance_metrics():
        """Display performance metrics in sidebar"""
        if not hasattr(st.session_state, 'performance_metrics'):
            return
        
        with st.sidebar.expander("⚡ Performance Metrics"):
            metrics = st.session_state.performance_metrics
            
            for func_name, data in metrics.items():
                st.write(f"**{func_name}**")
                st.write(f"Time: {data['execution_time']:.2f}s")
                st.write(f"Memory: {data['memory_used']:.1f}MB")
                st.write(f"Status: {'✅' if data['success'] else '❌'}")
                st.write("---")
    
    @staticmethod
    def optimize_plotly_figures(fig):
        """Optimize Plotly figures for better performance"""
        # Reduce data points for large datasets
        for trace in fig.data:
            if hasattr(trace, 'x') and len(trace.x) > 1000:
                # Downsample large datasets
                step = len(trace.x) // 1000
                trace.x = trace.x[::step]
                if hasattr(trace, 'y'):
                    trace.y = trace.y[::step]
        
        # Optimize layout
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=30, b=0),
            autosize=True
        )
        
        return fig
    
    @staticmethod
    def preload_critical_data():
        """Preload critical data for faster access"""
        if 'critical_data_loaded' not in st.session_state:
            # Preload common room types
            st.session_state.room_types = [
                'Living Room', 'Bedroom', 'Kitchen', 'Bathroom', 
                'Office', 'Dining Room', 'Closet', 'Hallway'
            ]
            
            # Preload common furniture sizes
            st.session_state.furniture_sizes = {
                'desk': (1.5, 0.8),
                'bed': (2.0, 1.5),
                'sofa': (2.5, 1.0),
                'table': (1.2, 0.8),
                'chair': (0.6, 0.6)
            }
            
            st.session_state.critical_data_loaded = True
    
    @staticmethod
    def batch_process_zones(zones, batch_size=10):
        """Process zones in batches for better performance"""
        results = []
        total_batches = len(zones) // batch_size + (1 if len(zones) % batch_size else 0)
        
        progress_bar = st.progress(0)
        
        for i in range(0, len(zones), batch_size):
            batch = zones[i:i + batch_size]
            
            # Process batch
            batch_results = []
            for zone in batch:
                # Process individual zone
                batch_results.append(zone)
            
            results.extend(batch_results)
            
            # Update progress
            progress = (i // batch_size + 1) / total_batches
            progress_bar.progress(progress)
        
        progress_bar.empty()
        return results

# Global performance monitoring
def init_performance_monitoring():
    """Initialize performance monitoring"""
    if 'performance_optimizer' not in st.session_state:
        st.session_state.performance_optimizer = PerformanceOptimizer()
        
        # Preload critical data
        PerformanceOptimizer.preload_critical_data()
        
        # Start memory optimization
        PerformanceOptimizer.optimize_memory()

# Performance decorators for common functions
performance_monitor = PerformanceOptimizer.monitor_performance
cache_computation = PerformanceOptimizer.cache_large_computations
async_process = PerformanceOptimizer.async_processing