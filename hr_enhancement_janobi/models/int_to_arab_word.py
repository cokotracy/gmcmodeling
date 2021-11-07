"""
 * ----------------------------------------------------------------------
 *
 * Copyright (C) 2009 by Khaled Al-Shamaa.
 *
 * http://www.ar-php.org
 *
 * ----------------------------------------------------------------------
 *
 * LICENSE
 *
 * This program is open source product; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public License (LGPL)
 * as published by the Free Software Foundation; either version 3
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/lgpl.txt>.
 *
 * ----------------------------------------------------------------------
 *
 * Class Name: Spell numbers in the Arabic idiom
 *
 * Filename:   ArNumbers.class.php
 *
 * Original    Author(s): Khaled Al-Sham'aa <khaled.alshamaa@gmail.com>
 *
 * Purpose:    Spell numbers in the Arabic idiom
 *
 * ----------------------------------------------------------------------
 *
 * Spell numbers in the Arabic idiom
 *
 * PHP class to spell numbers in the Arabic idiom. This function is very
 * useful for financial applications in Arabic for example.
 *
 * If you ever have to create an Arabic PHP application built around invoicing or
 * accounting, you might find this class useful. Its sole reason for existence is
 * to help you translate integers into their spoken-word equivalents in Arabic
 * language.
 *
 * How is this useful? Well, consider the typical invoice: In addition to a
 * description of the work done, the date, and the hourly or project cost, it always
 * includes a total cost at the end, the amount that the customer is expected to pay.
 * To avoid any misinterpretation of the total amount, many organizations (mine
 * included) put the amount in both words and figures; for example, 1,200 becomes
 * "one thousand and two hundred dollars." You probably do the same thing every time
 * you write a check.
 *
 * Now take this scenario to a Web-based invoicing system. The actual data used to
 * generate the invoice will be stored in a database as integers, both to save space
 * and to simplify calculations. So when a printable invoice is generated, your Web
 * application will need to convert those integers into words, this is more clarity
 * and more personality.
 *
 * This class will accept almost any numeric value and convert it into an equivalent
 * string of words in written Arabic language (using Windows-1256 character set).
 * The value can be any positive number up to 999,999,999 (users should not use
 * commas). It will take care of feminine and Arabic grammar rules.
 *
 * Example:
 * <code>
 *     include('./Arabic.php');
 *     Arabic = new Arabic('ArNumbers');
 *
 *     Arabic->ArNumbers->setFeminine(1);
 *     Arabic->ArNumbers->setFormat(1);
 *
 *     integer = 2147483647;
 *
 *     text = Arabic->int2str(integer);
 *
 *     echo "<p align=\"right\"><b class=hilight>integer</b><br />text</p>";
 *
 *     Arabic->ArNumbers->setFeminine(2);
 *     Arabic->ArNumbers->setFormat(2);
 *
 *     integer = 2147483647;
 *
 *     text = Arabic->int2str(integer);
 *
 *     echo "<p align=\"right\"><b class=hilight>integer</b><br />text</p>";
 * </code>
 *
 * @category  Text
 * @package   Arabic
 * @author    Khaled Al-Shamaa <khaled.alshamaa@gmail.com>
 * @copyright 2009 Khaled Al-Shamaa
 *
 * @license   LGPL <http://www.gnu.org/licenses/lgpl.txt>
 * @link      http://www.ar-php.org
 """

# New in PHP V5.3: Namespaces
# namespace Arabic/ArNumbers;

"""
 * This PHP class spell numbers in the Arabic idiom
 *
 * @category  Text
 * @package   Arabic
 * @author    Khaled Al-Shamaa <khaled.alshamaa@gmail.com>
 * @copyright 2009 Khaled Al-Shamaa
 *
 * @license   LGPL <http://www.gnu.org/licenses/lgpl.txt>
 * @link      http://www.ar-php.org
 """
import unicodedata
import math


class ArNumbers:
    _individual = {};
    _feminine = 1;
    _format = 1;

    ##"""
    ##     * Loads initialize values
    ##"""
    def __init__(self):
        self._individual[0] = {};
        self._individual[1] = {};
        self._individual[2] = {};
        self._individual[2][1] = {};
        self._individual[2][2] = {};
        self._individual[3] = {};
        self._individual[4] = {};
        self._individual[5] = {};
        self._individual[6] = {};
        self._individual[7] = {};
        self._individual[8] = {};
        self._individual[9] = {};
        self._individual[10] = {};
        self._individual[11] = {};
        self._individual[12] = {};
        self._individual[12][1] = {};
        self._individual[12][2] = {};
        self._individual[13] = {};
        self._individual[14] = {};
        self._individual[15] = {};
        self._individual[16] = {};
        self._individual[17] = {};
        self._individual[18] = {};
        self._individual[19] = {};
        self._individual[20] = {};
        self._individual[30] = {};
        self._individual[40] = {};
        self._individual[50] = {};
        self._individual[60] = {};
        self._individual[70] = {};
        self._individual[80] = {};
        self._individual[90] = {};
        self._individual[100] = {};
        self._individual[200] = {};
        self._individual[300] = {};
        self._individual[400] = {};
        self._individual[500] = {};
        self._individual[600] = {};
        self._individual[700] = {};
        self._individual[800] = {};
        self._individual[900] = {};
        self._individual[1000] = {};
        self._individual[2000] = {};
        self._individual[14] = {};
        self._individual[0][1] = u'';
        self._individual[0][2] = u'';
        self._individual[1][1] = u'واحد';
        self._individual[1][2] = u'واحدة';
        self._individual[2][1][1] = u'إثنان';
        self._individual[2][1][2] = u'إثنين';
        self._individual[2][2][1] = u'إثنتان';
        self._individual[2][2][2] = u'إثنتين';

        self._individual[3][1] = u'ثلاثة';
        self._individual[4][1] = u'أربعة';
        self._individual[5][1] = u'خمسة';
        self._individual[6][1] = u'ستة';
        self._individual[7][1] = u'سبعة';
        self._individual[8][1] = u'ثمانية';
        self._individual[9][1] = u'تسعة';
        self._individual[10][1] = u'عشرة';
        self._individual[3][2] = u'ثلاثة';
        self._individual[4][2] = u'أربعة';
        self._individual[5][2] = u'خمسة';
        self._individual[6][2] = u'ستة';
        self._individual[7][2] = u'سبعة';
        self._individual[8][2] = u'ثمانية';
        self._individual[9][2] = u'تسعة';
        self._individual[10][2] = u'عشرة';

        self._individual[11][1] = u'أحد عشر';
        self._individual[11][2] = u'إحدى عشرة';

        self._individual[12][1][1] = u'إثنا عشر';
        self._individual[12][1][2] = u'إثني عشر';
        self._individual[12][2][1] = u'إثنتا عشرة';
        self._individual[12][2][2] = u'إثنتي عشرة';

        self._individual[13][1] = u'ثلاثة عشر';
        self._individual[14][1] = u'أربعة عشر';
        self._individual[15][1] = u'خمسة عشر';
        self._individual[16][1] = u'ستة عشر';
        self._individual[17][1] = u'سبعة عشر';
        self._individual[18][1] = u'ثمانية عشر';
        self._individual[19][1] = u'تسعة عشر';
        self._individual[13][2] = u'ثلاثة عشر';
        self._individual[14][2] = u'أربعة عشر';
        self._individual[15][2] = u'خمسة عشر';
        self._individual[16][2] = u'ستة عشر';
        self._individual[17][2] = u'سبعة عشر';
        self._individual[18][2] = u'ثمانية عشر';
        self._individual[19][2] = u'تسعة عشر';

        self._individual[20][1] = u'عشرون';
        self._individual[30][1] = u'ثلاثون';
        self._individual[40][1] = u'أربعون';
        self._individual[50][1] = u'خمسون';
        self._individual[60][1] = u'ستون';
        self._individual[70][1] = u'سبعون';
        self._individual[80][1] = u'ثمانون';
        self._individual[90][1] = u'تسعون';
        self._individual[20][2] = u'عشرين';
        self._individual[30][2] = u'ثلاثين';
        self._individual[40][2] = u'أربعين';
        self._individual[50][2] = u'خمسين';
        self._individual[60][2] = u'ستين';
        self._individual[70][2] = u'سبعين';
        self._individual[80][2] = u'ثمانين';
        self._individual[90][2] = u'تسعين';

        self._individual[200][1] = u'مئتان';
        self._individual[200][2] = u'مئتين';

        self._individual[100] = u'مائة';
        self._individual[300] = u'ثلاثمائة';
        self._individual[400] = u'أربعمائة';
        self._individual[500] = u'خمسمائة';
        self._individual[600] = u'ستمائة';
        self._individual[700] = u'سبعمائة';
        self._individual[800] = u'ثمانمائة';
        self._individual[900] = u'تسعمائة';
        self.complications = {1: {}, 2: {}, 3: {}};
        self.complications[1][1] = u'ألفان';
        self.complications[1][2] = u'ألفين';
        self.complications[1][3] = u'آلاف';
        self.complications[1][4] = u'ألف';

        self.complications[2][1] = u'مليونان';
        self.complications[2][2] = u'مليونين';
        self.complications[2][3] = u'ملايين';
        self.complications[2][4] = u'مليون';

        self.complications[3][1] = u'ملياران';
        self.complications[3][2] = u'مليارين';
        self.complications[3][3] = u'مليارات';
        self.complications[3][4] = u'مليار';

    ##    """
    ##     * Set feminine flag of the counted object
    ##     *
    ##     * @param integer value Counted object feminine (1 for masculine & 2 for feminine)
    ##     *
    ##     * @return boolean True if success, or False if fail
    ##     * @author Khaled Al-Shamaa <khaled.alshamaa@gmail.com>
    ##     """
    def setFeminine(self, value):
        flag = True;
        if (value == 1 or value == 2):
            self._feminine = value;
        else:
            flag = False;
        return flag;

    ##    """
    ##     * Set the grammar position flag of the counted object
    ##     *
    ##     * @param integer value Grammar position of counted object
    ##     *                       (1 if Marfoua & 2 if Mansoub or Majrour)
    ##     *
    ##     * @return boolean True if success, or False if fail
    ##     * @author Khaled Al-Shamaa <khaled.alshamaa@gmail.com>
    ##     """
    def setFormat(self, value):
        flag = True;

        if (value == 1 or value == 2):
            self._format = value;
        else:
            flag = False;
        return flag;

    ##"""
    ##     * Get the feminine flag of counted object
    ##     *
    ##     * @return integer return current setting of counted object feminine flag
    ##     * @author Khaled Al-Shamaa <khaled.alshamaa@gmail.com>
    ##"""
    def getFeminine(self):
        return self._feminine;

    """
     * Get the grammer position flag of counted object
     *
     * @return integer return current setting of counted object grammer
     *                 position flag
     * @author Khaled Al-Shamaa <khaled.alshamaa@gmail.com>
     """

    def getFormat(self):
        return self._format;

    ##    """
    ##     * Spell integer number in Arabic idiom
    ##     *
    ##     * @param integer number        The number you want to spell in Arabic idiom
    ##     * @param string  outputCharset (optional) Output charset [utf-8|windows-1256|iso-8859-6]
    ##     *                               default value is None (use set output charset)
    ##     * @param object  main          Main Ar-PHP object to access charset converter options
    ##     *
    ##     * @return string The Arabic idiom that spells inserted number
    ##     * @author Khaled Al-Shamaa <khaled.alshamaa@gmail.com>
    ##     """
    def int2str(self, number, outputCharset=None, main=None):
        ##		temp = (trunc(number), number-trunc(number));
        temp = number.split('.');
        string = self._int2str(temp[0]);
        if (len(temp) > 1):
            if len(temp[1]) == 1:
                temp[1] += '0'
            dec = self._int2str(temp[1]);
            string += u' فاصلة ' + dec;
        if (main):
            if (outputCharset == None):
                outputCharset = main.getOutputCharset();
            string = main.coreConvert(string, 'utf-8', outputCharset);
        return string;

    """
     * Spell integer number in Arabic idiom
     *
     * @param integer number The number you want to spell in Arabic idiom
     *
     * @return string The Arabic idiom that spells inserted number
     * @author Khaled Al-Shamaa <khaled.alshamaa@gmail.com>
     """

    def _int2str(self, number):
        blocks = [];
        items = [];
        string = u'';
        number = number;  # trunc(int(number)) #(int)number);
        try:
            newnumber = int(number);
        except:
            number = "0";
        if (int(number) > 0):
            while (len(number) > 3):
                blocks.append(number[-3:]);
                number = number[:len(number) - 3];
            blocks.append(number);
            blocks_num = len(blocks) - 1;
            i = blocks_num;
            while i >= 0:  # (i = blocks_num; i >= 0; i--) :
                number = math.floor(int(blocks[i]));
                text = self._writtenBlock(number);
                if (text):
                    if (number == 1 and i != 0):
                        text = self.complications[i][4];
                    elif (number == 2 and i != 0):
                        text = self.complications[i][self._format];
                    elif (number > 2 and number < 11 and i != 0):
                        text += u' ' + self.complications[i][3];
                    elif (i != 0):
                        text += u' ' + self.complications[i][4];
                    items.append(text);
                i -= 1;
            string = u' و '.join(items);
        else:
            string = u'صفر';
        return string;

    """
     * Spell sub block number of three digits max in Arabic idiom
     *
     * @param integer number Sub block number of three digits max you want to
     *                        spell in Arabic idiom
     *
     * @return string The Arabic idiom that spells inserted sub block
     * @author Khaled Al-Shamaa <khaled.alshamaa@gmail.com>
     """

    def _writtenBlock(self, number):
        items = [];
        string = u'';
        number = int(number)
        if (number > 99):
            hundred = math.floor(number / 100) * 100;
            number = number % 100;

            if (hundred == 200):
                items.append(self._individual[hundred][self._format]);
            else:
                items.append(self._individual[hundred]);
        if (number == 2 or number == 12):
            items.append(self._individual[number][self._feminine][self._format]);
        elif (number < 20):
            items.append(self._individual[int(number)][self._feminine]);
        else:
            ones = number % 10;
            tens = math.floor(number / 10) * 10;
            tens = int(tens);

            if (ones == 2):
                items.append(self._individual[ones][self._feminine][self._format]);
            elif (ones > 0):
                items.append(self._individual[ones][self._feminine]);
            items.append(self._individual[tens][self._format]);

        if u'' in items: items.remove(u'');
        string = u' و '.join(items);
        return string;

    def text2number(text):
        """
        Convert arabic text into number, for example convert تسعة وعشرون  =>29.
        @param text: input text
        @type text: unicode
        @return : number extracted from text
        @rtype: integer
        >>> text2number(u"خمسمئة وثلاث وعشرون");
        523
        """
        # the result total is 0
        total = 0;
        # the partial total for the three number
        partial = 0;
        words = text.split(' ');
        for word in words:
            if ThaousandMultiple.has_key(word):
                total += partial * ThaousandMultiple[word];
                # re-initiate the partial total
                partial = 0;
            if NumberWords.has_key(word):
                partial += NumberWords[word];
        # add the final partial to total
        total += partial;
        return total


# Added by Cubex Team
# from: http://stackoverflow.com/questions/26626238/how-to-convert-normal-numbers-into-arabic-numbers-in-django
arabic_indic_trans = dict(
    zip((ord(s) for s in u'0123456789'),
        u'\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669')
)


# convert to arabic digits
def to_arabic_digits(value):
    s = value
    if isinstance(value, float):
        if value == round(value):
            s = "{:,d}".format(int(value))
        else:
            s = "{:,.2f}".format(value)

    return unicode(s).translate(arabic_indic_trans)
