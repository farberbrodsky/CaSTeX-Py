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
            if final_x == None:
                return prev_final_x
            prev_final_x = final_x
            final_x = final_x.simplified()
            if type(final_x) == type(prev_final_x) and same_exactly(final_x, prev_final_x):
                return final_x
    except:
        return final_x


def simplify_once(x):
    try:
        return x.simplified()
    except:
        return x


def approx(x):
    try:
        return x.approx()
    except:
        return x


def same_exactly(x, y):
    if (type(x) == int and type(y) == int) or (type(x) == float and type(y) == float):
        return x == y
    try:
        return x.same_exactly(y)
    except:
        return False


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

    def same_exactly(self, other):
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
        ra = simplify_once(self.a)  # result a
        rb = simplify_once(self.b)  # result b

        if type(ra) is not int or type(rb) is not int:
            # support type-specific simplifications
            try:
                x = ra / rb
                if x != None:
                    return x
            except:
                pass

        try:
            try:
                final_gcd = ra.__gcd__(rb)
            except:
                final_gcd = gcd(ra, rb)
            if final_gcd == None:
                return Fraction(ra, rb)
            if isinstance(ra, int):
                ra //= final_gcd
            else:
                ra /= final_gcd
            if isinstance(rb, int):
                rb //= final_gcd
            else:
                rb /= final_gcd
        except:
            pass
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
            return Fraction(self.a * other.a, self.b * other.b)
        elif isinstance(other, type(self.a)):
            return Fraction(self.a * other, self.b)
        else:
            return Multiplication([self, other])

    def __truediv__(self, other):
        if isinstance(other, Fraction):
            return Fraction(self.a * other.b, self.b * other.a)
        else:
            return Fraction(self.a, self.b * other)

    def __mod__(self, other):
        return self - other * (self / other).whole_part()

    def __neg__(self):
        try:
            return Fraction(self.a.__neg__(), self.b)
        except AttributeError:
            return Fraction(self.a, self.b.__neg__())

    def __eq__(self, other):
        if type(other) is Fraction:
            my_simplified = self.simplified()
            other_simplified = other.simplified()
            return (my_simplified.a == other_simplified.a and
                    my_simplified.b == other_simplified.b)
        elif self.a == 0 and other == 0:
            return True
        return False

    def same_exactly(self, other):
        return type(other) is Fraction and same_exactly(self.a, other.a) and same_exactly(self.b, other.b)

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

                return Addition([simplify_once(x) for x in result])

        return Addition([simplify_once(x) for x in self.parts])

    def __add__(self, other):
        if type(other) is Addition:
            return Addition(self.parts + other.parts)
        else:
            return Addition(self.parts + [other])

    def __mul__(self, other):
        if type(other) is Addition:
            # Multiply every item in other by self and add it
            new_parts = []
            try:
                for item in other:
                    new_parts.append(self * item)
                return Addition(new_parts)
            except:
                # Just a regular multiplication
                return Multiplication([self, other])
        else:
            # Try to multiply other by everything
            new_parts = []
            try:
                for part in self.parts:
                    new_parts.append(part * other)
                return Addition(new_parts)
            except:
                # Just a regular multiplication
                return Multiplication([self, other])

    def __neg__(self):
        return Addition([-x for x in self.parts])

    def __str__(self):
        return "+".join(["(" + str(p) + ")" for p in self.parts])

    def same_exactly(self, other):
        if type(self) == type(other) and len(self.parts) == len(other.parts):
            for part1, part2 in zip(self.parts, other.parts):
                if not same_exactly(part1, part2):
                    return False
            return True
        return False


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
                    try:
                        x = b * a
                        if x is not None and not type(x) is Multiplication:
                            found_b = True
                    except:
                        pass

            if found_b:
                result = self.parts + [x]
                if a_index > b_index:
                    del result[a_index]
                    del result[b_index]
                else:
                    del result[b_index]
                    del result[a_index]

                return Multiplication([simplify_once(x) for x in result])

        return Multiplication([simplify_once(x) for x in self.parts])

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

    def same_exactly(self, other):
        if type(self) == type(other) and len(self.parts) == len(other.parts):
            for part1, part2 in zip(self.parts, other.parts):
                if not same_exactly(part1, part2):
                    return False
            return True
        return False


class Power(DefaultOperators):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def approx(self):
        return approx(self.a) ** approx(self.b)

    def simplified(self):
        if type(self.b) is int and self.b >= 1:
            # Try to multiply a by itself many times
            try:
                result = self.a
                for _ in range(self.b - 1):
                    result = result * self.a
                return result
            except:
                pass

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
            return Power(simplify_once(self.a), simplify_once(self.b))

    def __mul__(self, other):
        # a^m * a^n = a^(m+n)
        if type(other) is Power and self.a == other.a:
            return Power(self.a, other.a + other.b)
        else:
            return Multiplication([self, other])

    def __str__(self):
        return "(" + str(self.a) + ")^{" + str(self.b) + "}"

    def same_exactly(self, other):
        return type(other) is Power and same_exactly(self.a, other.a) and same_exactly(self.b, other.b)

# TODO make irrational classes like Pi and E


class Complex(DefaultOperators):
    def __init__(self, re, im):
        self.re = re
        self.im = im

    def approx(self):
        return Complex(approx(self.re), approx(self.im))

    def simplified(self):
        if self.im == 0:
            return self.re
        return Complex(simplify_once(self.re), simplify_once(self.im))

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
            try:
                re = self.re * other
            except:
                re = other * self.re

            try:
                im = self.im * other
            except:
                im = other * self.im

            return Complex(re, im)

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
        if self.re != 0:
            return str(self.re) + "+(" + str(self.im) + ")i"
        return "(" + str(self.im) + ")i"

    def same_exactly(self, other):
        return type(other) is Complex and same_exactly(self.re, other.re) and same_exactly(self.im, other.im)
