def gcd(a, b):
    if b == 0:
        return a
    else:
        return gcd(b, a % b)

def simplify(x):
    # Simplify until it doesn't do anything or you can't simplify
    prev_final_x = x
    final_x = x
    try:
        while True:
            prev_final_x = final_x
            final_x = final_x.simplified()
            if final_x == prev_final_x:
                return final_x
    except:
        return final_x

class Fraction:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def whole_and_fraction(self):
        # Seperates 15/4 to 3, 3/4
        fraction_part = Fraction(self.a % self.b, self.b)
        whole_part = self - fraction_part
        return (whole_part, fraction_part)

    def whole_part(self):
        return self.whole_and_fraction()[0]
    
    def fraction_part(self):
        return self.whole_and_fraction()[1]

    def simplified(self):
        ra = self.a # result a
        rb = self.b # result b
        try:
            final_gcd = ra.__gcd__(rb)
        except:
            final_gcd = gcd(ra, rb)
        if type(ra) is int:
            ra //= final_gcd
        else:
            ra /= final_gcd
        if type(rb) is int:
            rb //= final_gcd
        else:
            rb /= final_gcd
        
        # Type-specific simplifications
        if type(ra) is Complex and type(rb) is Complex:
            # Multiply both by the conjugate of the divisor
            ra *= rb.conjugate()
            rb *= rb.conjugate()
            complex_gcd = ra.__gcd__(rb)
            ra /= complex_gcd
            rb /= complex_gcd
            # Check whether rb is still complex, otherwise we can make it not complex
            if rb.im == 0:
                return ra / rb.re
        return Fraction(ra, rb)

    def __add__(self, other):
        if type(other) is Fraction:
            return simplify(Fraction(self.a * other.b + self.b * other.a, self.b * other.b))
        else:
            return simplify(Fraction(self.a + other * self.b, self.b))

    def __sub__(self, other):
        return self + other.__neg__()

    def __mul__(self, other):
        if type(other) is Fraction:
            return simplify(Fraction(self.a * other.a, self.b * other.b))
        else:
            return simplify(Fraction(self.a * other, self.b))

    def __truediv__(self, other):
        if type(other) is Fraction:
            return simplify(Fraction(self.a * other.b, self.b * other.a))
        else:
            return simplify(Fraction(self.a, self.b * other))

    def __mod__(self, other):
        return simplify(self - other * (self / other).whole_part())

    def __neg__(self):
        try:
            return Fraction(self.a.__neg__(), self.b)
        except AttributeError:
            return Fraction(self.a, self.b.__neg__())

    def __eq__(self, other):
        if other is Fraction:
            return self.a == other.a and self.b == other.b
        else:
            return self.a / self.b == other

    def __str__(self):
        if self.b == 1:
            return str(self.a)
        else:
            return r"\frac{" + str(self.a) + "}{" + str(self.b) + "}"

class Addition:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def simplified(self):
        try:
            return self.a + self.b
        except:
            return Addition(simplify(self.a), simplify(self.b))

    def __add__(self, other):
        # Try to add it to either A or B
        ra = self.a  # result a
        rb = self.b  # result b
        could_add = False

        try:
            ra += other
            could_add = True
        except:
            try:
                rb += other
                could_add = True
            except:
                pass

        if could_add:
            return Addition(ra, rb)
        else:
            return Addition(Addition(self.a, self.b), other)

    def __sub__(self, other):
        # Try to subtract it from either A or B
        ra = self.a  # result a
        rb = self.b  # result b
        could_sub = False

        try:
            ra -= other
            could_sub = True
        except:
            try:
                rb -= other
                could_sub = True
            except:
                pass

        if could_sub:
            return Addition(ra, rb)
        else:
            return Addition(Addition(self.a, self.b), -other)

       
    
    # TODO implement add, sub, mul, truediv, mod, neg, eq

    def __str__(self):
        return "(" + str(self.a) + ")+(" + str(self.b) + ")"


class Power:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    # TODO implement all the algebra functions here, add, sub, mul, truediv, mod, neg

# TODO make irrational classes like Pi and E

class Complex:
    def __init__(self, re, im):
        self.re = re
        self.im = im

    def __add__(self, other):
        if type(other) is Complex:
            return Complex(self.re + other.re, self.im + other.im)
        else:
            return Complex(self.re + other, self.im)

    def __sub__(self, other):
        return self + other.__neg__()

    def __mul__(self, other):
        if type(other) is Complex:
            return Complex(
                self.re * other.re - self.im * other.im,
                self.re * other.im + self.im * other.re
            )
        else:
            return Complex(self.re * other, self.im * other)

    def __truediv__(self, other):
        if type(other) is Complex:
            return simplify(Fraction(self, other))
        else:
            return Complex(self.re / other, self.im / other)

    def __gcd__(self, other):
        return gcd(gcd(self.re, other.re), gcd(self.im, other.im))

    def __neg__(self):
        return Complex(-self.re, -self.im)

    def conjugate(self):
        return Complex(self.re, -self.im)
    
    def __eq__(self, other):
        if other is Complex:
            return self.re == other.re and self.im == other.im
        elif self.im == 0:
            return self.re == other
        return False

    def __str__(self):
        return str(self.re) + "+" + str(self.im) + "i"

x = Addition(Complex(Fraction(5, 1), Fraction(2, 1)) / Complex(Fraction(7, 1), Fraction(4, 1)), 1)

print(simplify(x))
