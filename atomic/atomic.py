import sys
import functools
from threading import Lock, currentThread


class AtomicException(Exception):
    """base exception class"""    
    pass

class AtomicTimeoutException( AtomicException ):
    pass

class AtomicRefCountException( AtomicException ):
    pass

class AtomicNotLockedException( AtomicException ):
    pass

class AtomicBaseClassException( AtomicException ):
    pass

class AtomicOwnerException( AtomicException ):
    pass


class _Lock_Context():
    
    def __init__(self,atomic):
        self.atomic=atomic
        
    def __enter__(self):
        self.atomic._enter__impl()

    def __exit__(self, exception_type, exception_value, traceback):
        self.atomic._exit__impl(exception_type, exception_value, traceback)


class Atomic():
    
    def __init__(self,timeout=-1,trace_on=False):
        self._trace_atomic = trace_on
        
        # use Lock here since RLock does not have a locked() peek function
        ## todo: change to RLock to reduce implementation effort (?)
        self._lock_atomic = Lock()
        
        self._timeout_atomic = timeout
        self._lock_count_atomic = 0
        self._owner_thread = None
        self._acquired = False
        
    # helper shorthand

    def _thread_id(self):
        return currentThread().ident
    
    # locking

    def _trylock(self):
        if self._owner_thread:
            if self._owner_thread != self._thread_id():
                raise AtomicOwnerException("lock owned by different thread" )
        if self._lock_count_atomic == 0:
            self._acquired = self._lock_atomic.acquire(timeout=self._timeout_atomic)
            if self._acquired:
                self._owner_thread = self._thread_id()
        else:
            self._print_t( f"lock counter increased = {self._lock_count_atomic}" )
        if self._acquired:
            self._lock_count_atomic += 1
        self._print_t( "acquired lock =", self._acquired,", thread#", self._owner_thread )
        return self._acquired
        
    def _release(self):
        if not self.locked():
            raise AtomicNotLockedException("you need to lock the object before")
        if self._owner_thread != self._thread_id():
            raise AtomicOwnerException("can not release object locked by different thread")
        self._lock_count_atomic -= 1
        if self._lock_count_atomic > 0:
            self._print_t( "lock counter decreased", self._lock_count_atomic,", thread#", self._owner_thread )
            return
        self._acquired = False
        thread = self._owner_thread
        self._owner_thread = None
        self._lock_atomic.release()
        self._print_t( "released lock", "thread#", thread )
        
    def locked(self):
        """
            check if lock was aquired before
        """
        self._acquired = self._lock_atomic.locked()
        return self._acquired
    
    # trace
    
    def trace(self,trace_on=False):
        """
            set trace level
        """
        self._trace_atomic = trace_on
        
    def _print_t(self,*args):
        """internal print trace function"""
        try:
            if self._trace_atomic:
                print( "(trace) ", *args )                
        except AttributeError as ex:            
            raise AtomicBaseClassException("make sure to call atomic's super().__init__() before")
        
    # context manager
    
    def openlocked(self):
        return _Lock_Context(self)
        
    def _enter__impl(self):
        self._print_t("enter context")        
        self._trylock()
        if not self.locked():
            raise AtomicException("could no aquire lock")
        return self
        
    def _exit__impl(self, exception_type, exception_value, traceback):
        self._print_t("exit context")
        self._release()
        
    # wait notify
    
    def wait(self,timeout=None):
        self._lock_atomic.wait(timeout)
        
    def notify(self,n=1):
        self._lock_atomic.notify(n)
        
    # decorator
    
    def LockFunc(f):
        """
            decorator for locking on function call level
            the lock focus is on object instance level
            one call to any decorated function of a object instance will lock the whole instance against usage of other threads
            
            use as:
            
            @Atomic.LockFunc
            def special_function_with_lock_atomicing():
                pass       
            
        """
        @functools.wraps(f)
        def _atomic_wrapper(*argv,**kwargs):
            # check if base class is propper
            self_ref = argv[0]
            if not isinstance( self_ref, Atomic ):
                raise AtomicBaseClassException("no atomic base class found")
            try:
                self_ref._print_t( "enter decorated call to", f.__name__, ":", f )
                # call within an internal context
                with self_ref.openlocked() as _f_lock_atomic:
                    if self_ref._timeout_atomic <= 0 and not self_ref._acquired:
                        raise AtomicTimeoutException("timeout, could not acuire lock")
                    # call the wrapped funcction
                    return f(*argv,**kwargs)
            finally:
                self_ref._print_t( "leave decorated call to", f.__name__, ":", f )
        return _atomic_wrapper
    
    # code execution

    def exe(self, callback = None ):
        """
            execute a program within a lock
        """
        self._trylock()
        try:
            if self.locked():
                if callback != None:
                    self._print_t("before custom callback")
                    callback( )
                    self._print_t("after custom callback")
                else:
                    self._print_t("before callback")
                    self.callback()
                    self._print_t("after callback")
            else:
                raise AtomicException("could no aquire lock")
        finally:
            self._release()

    def callback(self):
        """
            callback for custom function if called without parameter
            
                obj.exe()
        """
        raise AtomicException("your implementation is missing!")


