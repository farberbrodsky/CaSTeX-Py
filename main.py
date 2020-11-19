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


def approx(x):
    try:
        return x.approx()
    except:
        return x


class DefaultOperators:
    def __add__(self, other):
        return Addition([self, other])

    def __sub__(self, other):
        return self + other.__neg__()

    def __mul__(self, other):
        return Multiplication([self, other])

    def __rmul__(self, other):
        return other.__mul__(self)

    def __truediv__(self, other):
        return Fraction(self, other)

    def __eq__(self, other):
        return str(self) == str(other)


class Fraction(DefaultOperators):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def approx(self):
        return approx(self.a) / approx(self.b)

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
        ra = self.a  # result a
        rb = self.b  # result b
        try:
            final_gcd = ra.__gcd__(rb)
        except:
            final_gcd = gcd(ra, rb)
        if isinstance(ra, int):
            ra //= final_gcd
        else:
            ra /= final_gcd
        if isinstance(rb, int):
            rb //= final_gcd
        else:
            rb /= final_gcd

        if (type(ra) is not int or type(rb) is not int):
            # support type-specific simplifications
            try:
                return ra / rb
            except:
                return Fraction(ra, rb)
        return Fraction(ra, rb)

    def __add__(self, other):
        if isinstance(other, Fraction):
            return Fraction(
                self.a *
                other.b +
                self.b *
                other.a,
                self.b *
                other.b
            )
        else:
            return Fraction(self.a + other * self.b, self.b)

    def __sub__(self, other):
        return self + other.__neg__()

    def __mul__(self, other):
        if isinstance(other, Fraction):
            return simplify(Fraction(self.a * other.a, self.b * other.b))
        else:
            return simplify(Fraction(self.a * other, self.b))

    def __truediv__(self, other):
        if isinstance(other, Fraction):
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


class Addition(DefaultOperators):
    def __init__(self, parts):
        self.parts = parts

    def approx(self):
        return sum(approx(x) for x in self.parts)

    def simplified(self):
        if len(self.parts) == 0:
            return 0
        elif len(self.parts) == 1:
            return self.parts[0]
        # Try to add different parts
        for a_index, a in enumerate(self.parts):
            found_b = False
            for b_index, b in enumerate(self.parts):
                if b_index == a_index:
                    continue
                try:
                    x = a + b
                    if x is not None and not type(x) is Addition:
                        found_b = True
                except:
                    pass

            if found_b:
                result = self.parts + [a + b]
                if a_index > b_index:
                    del result[a_index]
                    del result[b_index]
                else:
                    del result[b_index]
                    del result[a_index]

                return Addition([simplify(x) for x in result])

        return Addition([simplify(x) for x in self.parts])

    def __add__(self, other):
        if type(other) is Addition:
            return Addition(self.parts + other.parts)
        else:
            return Addition(self.parts + [other])

    def __neg__(self):
        return Addition([-x for x in self.parts])

    def __str__(self):
        return "+".join(["(" + str(p) + ")" for p in self.parts])


class Multiplication(DefaultOperators):
    def __init__(self, parts):
        self.parts = parts

    def approx(self):
        final = 1
        for x in self.parts:
            final = final * approx(x)
        return final

    def simplified(self):
        if len(self.parts) == 0:
            return 1
        elif len(self.parts) == 1:
            return self.parts[0]
        # Try to multiply different parts
        for a_index, a in enumerate(self.parts):
            found_b = False
            for b_index, b in enumerate(self.parts):
                if b_index == a_index:
                    continue
                try:
                    x = a * b
                    if x is not None and not type(x) is Multiplication:
                        found_b = True
                except:
                    pass

            if found_b:
                result = self.parts + [a * b]
                if a_index > b_index:
                    del result[a_index]
                    del result[b_index]
                else:
                    del result[b_index]
                    del result[a_index]

                return Multiplication([simplify(x) for x in result])

        return Multiplication([simplify(x) for x in self.parts])

    def __mul__(self, other):
        if type(other) is Multiplication:
            return Multiplication(self.parts + other.parts)
        else:
            return Multiplication(self.parts + [other])

    def __neg__(self):
        if len(self.parts) == 0:
            return Multiplication([])
        else:
            return Multiplication([-self.parts[0]] + self.parts[1:])

    def __str__(self):
        return "*".join(["(" + str(p) + ")" for p in self.parts])


class Power(DefaultOperators):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def approx(self):
        return approx(self.a) ** approx(self.b)

    def simplified(self):
        if self.a != 0 and self.b == 0:
            return 1
        elif self.b == 1:
            return self.a
        elif type(self.a) == Power:
            # (a^m)^n == a^(mn)
            return Power(self.a.a, self.a.b * self.b)
        elif type(self.a) == Multiplication:
            # (abc)^m = a^m * b^m * c^m
            return Multiplication([Power(a, self.b) for a in self.a.parts])
        else:
            return Power(simplify(self.a), simplify(self.b))

    def __mul__(self, other):
        # a^m * a^n = a^(m+n)
        if type(other) is Power and self.a == other.a:
            return Power(self.a, other.a + other.b)

    def __str__(self):
        return "(" + str(self.a) + ")^{" + str(self.b) + "}"
    # TODO does not support negatives

# TODO make irrational classes like Pi and E


class Complex(DefaultOperators):
    def __init__(self, re, im):
        self.re = re
        self.im = im

    def approx(self):
        return Complex(approx(self.re), approx(self.im))

    def __add__(self, other):
        if type(other) is Complex:
            return Complex(self.re + other.re, self.im + other.im)
        try:
            # Try adding to real
            return Complex(self.re + other, self.im)
        except:
            return Addition([self, other])

    def __mul__(self, other):
        if isinstance(other, Complex):
            return Complex(
                self.re * other.re - self.im * other.im,
                self.re * other.im + self.im * other.re
            )
        else:
            return Complex(self.re * other, self.im * other)

    def __truediv__(self, other):
        if isinstance(other, Complex):
            ra = self
            rb = other
            # Multiply both by the conjugate of the divisor
            ra *= rb.conjugate()
            rb *= rb.conjugate()
            complex_gcd = ra.__gcd__(rb)
            ra /= complex_gcd
            rb /= complex_gcd
            # Check whether rb is still complex, otherwise we can make it not
            # complex
            if rb.im == 0:
                return ra / rb.re
            return Fraction(ra, rb)
        else:
            try:
                return Complex(self.re / other, self.im / other)
            except:
                return Fraction(self, other)

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

# x = Multiplication([
#     Addition([
#         Complex(Fraction(1, 3), Fraction(1, 4)),
#         Complex(Fraction(5, 2), Fraction(6, 3)),
#         3
#     ]),
#     Complex(Fraction(0, 1), Fraction(1, 1)),
#     3
# ])
#
# x = Multiplication([Power(3, 0.5), Power(4, 3)])
#
# x = Multiplication([Power(3, 0.5), Power(3, 4)])
#
# x = Power(Multiplication([Fraction(2, 3), Fraction(4, 5)]), 3)
#
# print(x)
# print(simplify(x))
