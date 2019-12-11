
# Atomic locking

Atomic makes your code thread safe.
Just use the `@Atomic.LockFunc` decorator and derive your class from `Atomic` to lock easily object instances against unsynchronized access  

## Dependencies to other Python packages

No dependencies, pure Python.


## Code

The sample code produces some trace output on the console


    from atomic import *

    def sample():

        a = Atomic()
        with a.openlocked() as aa:
            print( f"locked?: {a.locked()}" )
        print( f"locked?: {a.locked()}" )

        # a complex class with locking on function level
        class complex_stuff(Atomic):
            
            def normal(self):
                print("normal")

            @Atomic.LockFunc
            def special(self):
                print("special")
                print("locked?",self.locked())

            @Atomic.LockFunc
            def special_complex(self):
                print("special complex")
                print("locked?",self.locked())
                # call another decorated lock function
                # internal lock counter will increased
                self.special()

            @Atomic.LockFunc
            def special_complex_sample(self):
                print("special complex")
                print("locked?",self.locked())
                # call another decorated lock function
                # internal lock counter will increased
                print("before with block")
                with self.openlocked() as lockself:
                    self.special()
                    
            def callback(self):
                print("inside callback")                


        cstuff = complex_stuff()

        #enable trace for this instance
        cstuff.trace(True)

        cstuff.normal()
        cstuff.special()
        cstuff.special_complex()
        cstuff.special_complex_sample()
        print( f"cstuff internal {cstuff._lock_count_atomic}" )

        with cstuff.openlocked():
            print()
            print( "call complex sample again from within a context" )
            cstuff.special_complex_sample()
            
        # perform the callback action
        cstuff.exe()
        
        cstuff.exe( callback = lambda : print("and now something completely different") )
            
        try:
            # this is not derived from Atomic
            class stuff_no_atomic_base(object):
                
                @Atomic.LockFunc
                def do_something():
                    """calling this will raise an exception"""
                    pass
                
            cbrk = stuff_no_atomic_base()
            cbrk.do_something()
        except Exception as ex:
            print(ex,file=sys.stderr)
        
        print("all done")


