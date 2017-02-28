#!/usr/bin/env python
#    chase 
#    Copyright (C) 2003 Bruce Woodward

#    chase is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.

#    chase is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#    along with chase; see the file COPYING. If not, write to the Free Software
#    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import DataSet
import utils
import Date


def day_of_the_week(date):
    ddate = Date.Date()
    year, month, dayofm = utils.split_date_string(date)
    ddate.year = year
    ddate.month = month
    ddate.day = dayofm
    return ddate.weekday() 

# find_first_day_of_week doesn't handle the case where there is only one day
# in the array even if that day is the first day of the week.
def find_first_day_of_week(ds):
    date = ds.get('date')
    for i in xrange(0, len(date)):
        if not are_dates_in_same_week(date[i],date[i-1]):
            return i
    else:
        raise "Couldn't find the start of the week"

def dates_from_daily_to_weekly(oldds, newds):
    date = []
    olddate = oldds.get('date')
    date.append(olddate[0])
    for i in xrange(1, len(olddate)):
        if not are_dates_in_same_week(olddate[i-1],olddate[i]):
            date.append(olddate[i])
    # the newds doesn't have the date dataseries for this function to be called
    # register the date series after it has been filled in because the DataSet
    # register method will automatically update the date_hash with the dates
    # just calculated.
    newds.register('date', date)

## dummy Date instances to avoid unnecessary instance creation.
__date1 = Date.Date()
__date2 = Date.Date()
def are_dates_in_same_week(d1, d2):
    """ takes two date values and returns true if the dates occur in the
    same week, false if they don't.
    """
    strd1 = str(int(d1))
    strd2 = str(int(d2))
    __date1.year, __date1.month, __date1.day = int(strd1[:3]), \
                                               int(strd1[4:6]), \
                                               int(strd1[6:])
    __date2.year, __date2.month, __date2.day = int(strd2[:3]), \
                                               int(strd2[4:6]), \
                                               int(strd2[6:])
    if __date2.ToJDNumber() - __date1.ToJDNumber() < 6 - day_of_the_week(d1):
        return 1
    else:
        return 0
    
def dates_from_daily_to_monthly(oldds, newds):
    pass


if __name__ == "__main__":
    import unittest

    class test(unittest.TestCase):
        def test_are_date_in_same_week(self):
            self.assertEquals(are_dates_in_same_week(20030101,20030102),1)
            self.assertEquals(are_dates_in_same_week(20030102,20030103),1)
            self.assertEquals(are_dates_in_same_week(20030103,20030106),0)
            self.assertEquals(are_dates_in_same_week(20030106,20030113),0)
            self.assertEquals(are_dates_in_same_week(20020228,20020301),1)
            
        def testDaily2Weekly(self):
            date= []
            open= []
            high= []
            low= []
            close= []
            for i in xrange(20021202, 20021205):
                date.append(i)
                open.append(10.0)
                high.append(10.2)
                low.append(9.8)
                close.append(9.9)
            self.assertEquals(open[0],10.0)
            dailyDataSet= DataSet.DataSet()
            dailyDataSet.register('date', date)
            dailyDataSet.register('open', open)
            self.assertEquals(dailyDataSet.get('open')[0], 10.0)
            dailyDataSet.register('high', high)
            dailyDataSet.register('low', low)
            dailyDataSet.register('close', close)
            newds= DataSet.DataSet()
            dates_from_daily_to_weekly(dailyDataSet, newds)
            self.assertEquals('date' in newds.get_headers(), 1)
            translatedDates= newds.get('date')
            self.assertEquals(len(translatedDates), 1)
            self.assertEquals(translatedDates[0], 20021202)
            self.assertEquals(dailyDataSet.get('open')[0], 10.0)
            self.assertEquals(dailyDataSet.get('close')[0], 9.9)

        def make_dates_and_dataset(self,dates):
            date= []
            for x in dates:
                date.append(x)
            dailyDataSet= DataSet.DataSet()
            dailyDataSet.register('date',date)
            newds= DataSet.DataSet()
            dates_from_daily_to_weekly(dailyDataSet, newds)
            return dates, dailyDataSet, newds

        ## Believed logic problem in the dates_from_daily_to_weekly
        ## function. The following tests should break until the logic is
        ## fixed.
        def testMissingDays1(self):
            date, dailyDataSet, newds = \
                  self.make_dates_and_dataset([20021202,20021203,20021204,
                                               20021211,20021212])
            translatedDates= newds.get('date')
            ## print translatedDates
            self.assertEquals(len(translatedDates),2)

        # the previous testMissingDays1 function didn't quite do the job.
        # see the comments for the drawable.testTranslateDayAheadNextWeek
        # test function.
        def testMissingDays2(self):
            date, dailyDataSet, newds = \
                  self.make_dates_and_dataset([20030106,20030107,20030116])
            self.assertEquals(len(newds.get('date')),2)

        #
        def testDaysSpaningAYear(self):
            date, dailyDataSet, newds = \
                      self.make_dates_and_dataset([20021230,20021231,20030101,
                                                   20030102])
            self.assertEquals(len(newds.get('date')),1)

    unittest.main()
            
