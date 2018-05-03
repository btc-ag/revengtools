using System;
using System.Collections;
using System.Collections.Generic;
using BTC.CAB.Commons.DateTime;
using BTC.CAB.TimeSeries.API.TestSupport;
using NUnit.Framework;

namespace BTC.CAB.TimeSeries.API.Test
{
    /// <summary>
    /// This is an abstract test class for different TimeSeriesEntryCursors
    /// </summary>
    [TestFixture]
    public abstract class AbstractGeneralTimeSeriesCursorTest
    {
        // =========================================================================================
        // ** Abstract Definitions *****************************************************************
        // =========================================================================================
        /// <summary>
        /// Inserts a TimeSeriesEntry at the given timeStamp.
        /// </summary>
        protected abstract void InsertDefaultEntryByTimeStamp(long timeStamp);

        /// <summary>
        /// Deletes the TimeSeriesEntry at the given timeStamp if one exists.
        /// </summary>
        protected abstract void DeleteDefaultEntryByTimeStamp(long timeStamp);

        /// <summary>
        /// A list of TimeStamps that are valid to insert into theDefaultTimeSeries.
        /// </summary>
        public abstract List<long> DefaultTimeStamps { get; }

        /// <summary>
        /// The DefaultTimeSeries having some default MetaData
        /// </summary>
        protected abstract ITimeSeries DefaultTimeSeries { get; }

        /// <summary>
        /// Checks if the given TimeSeriesEntry has the same values as the default TimeSeriesEntry
        /// inserted at given entries timeStamp.
        /// </summary>
        protected abstract void CheckEntry(ITimeSeriesEntry entry);

        /// <summary>
        /// The minimal available TimeStamp. For non-Regular TimeSeries this should 
        /// be DateTimeHelper.UtcMinValue.
        /// </summary>
        protected abstract long MinimumTimeStamp { get; }

        /// <summary>
        /// The maximal available TimeStamp. For non-Regular TimeSeries this should 
        /// be DateTimeHelper.UtcMaxValue.
        /// </summary>
        protected abstract long MaximumTimeStamp { get; }


        // =========================================================================================
        // ** Tests ********************************************************************************
        // =========================================================================================

        // *****************************************************************************************
        [Test]
        public void TestAaaCheckImplementation()
        {
            Assert.IsNotNull(DefaultTimeSeries);
            Assert.IsNotNull(DefaultTimeStamps);
            Assert.Greater(DefaultTimeStamps.Count, 1);

            Assert.AreEqual(0, DefaultTimeSeries.Count);
            InsertDefaultEntryByTimeStamp(DefaultTimeStamps[0]);
            Assert.AreEqual(1, DefaultTimeSeries.Count);
            DeleteDefaultEntryByTimeStamp(DefaultTimeStamps[0]);
            Assert.AreEqual(0, DefaultTimeSeries.Count);

            InsertAllDefaultEntries();
            Assert.AreEqual(DefaultTimeStamps.Count, DefaultTimeSeries.Count);
        }

        // *****************************************************************************************
        /// <summary>
        /// A test for Dispose
        /// </summary>
        [Test]
        public void TestActionsOnDisposedCursorFails()
        {
            ITimeSeriesEntryCursor cursor = CreateCursor();
            Assert.IsNull(cursor.Current);

            cursor.Dispose();

            foreach (OperationsHelper.CursorOperation cursorOperation in OperationsHelper.CursorOperations)
            {
                try
                {
                    cursorOperation(cursor);
                    Assert.Fail("The following operation should not work on a disposed cursor: " +
                                cursorOperation);
                }
                catch (ObjectDisposedException)
                {
                    // ok
                }
            }
        }


        // *****************************************************************************************
        /// <summary>
        /// A test for Reset
        /// </summary>
        [Test]
        public virtual void TestReset()
        {
            InsertDefaultEntryByIndex(0);
            IEnumerator<ITimeSeriesEntry> enumerator = CreateCursor();

        
            Assert.IsTrue(enumerator.MoveNext());
            ITimeSeriesEntry entry = enumerator.Current;

            enumerator.Reset();
            Assert.IsTrue(enumerator.MoveNext());
            Assert.IsTrue(TimeSeriesComparisons.CompareTimeSeriesEntry(entry, enumerator.Current));
        }

        // *****************************************************************************************
        /// <summary>
        /// A test for Reset
        /// </summary>
        [Test]
        public virtual void TestDoubleReset()
        {
            InsertDefaultEntryByIndex(0);
            IEnumerator<ITimeSeriesEntry> enumerator = CreateCursor();

            enumerator.Reset();
            Assert.IsTrue(enumerator.MoveNext());
            ITimeSeriesEntry entry = enumerator.Current;

            enumerator.Reset();
            Assert.IsTrue(enumerator.MoveNext());
            Assert.IsTrue(TimeSeriesComparisons.CompareTimeSeriesEntry(entry, enumerator.Current));
        }



        // *****************************************************************************************
        /// <summary>
        /// A test for SetToStart
        /// </summary>
        [Test]
        public virtual void TestSetToStart()
        {
            InsertDefaultEntryByIndex(0);
            ITimeSeriesEntryCursor cursor = CreateCursor();

            cursor.Reset();
            Assert.IsNull(cursor.Current);
            Assert.IsTrue(cursor.MoveNext());
            ITimeSeriesEntry entry = cursor.Current;

            cursor.SetToStart();
            Assert.IsTrue(cursor.MoveNext());
            Assert.IsTrue(TimeSeriesComparisons.CompareTimeSeriesEntry(entry, cursor.Current));
        }

        // *****************************************************************************************
        /// <summary>
        /// A test for SetToStart
        /// </summary>
        [Test]
        public virtual void TestDoubleSetToStart()
        {
            InsertDefaultEntryByIndex(0);
            ITimeSeriesEntryCursor cursor = CreateCursor();

            cursor.SetToStart();
            Assert.IsNull(cursor.Current);
            Assert.IsTrue(cursor.MoveNext());
            ITimeSeriesEntry entry = cursor.Current;

            cursor.SetToStart();
            Assert.IsTrue(cursor.MoveNext());
            Assert.IsTrue(TimeSeriesComparisons.CompareTimeSeriesEntry(entry, cursor.Current));
        }

        // *****************************************************************************************
        /// <summary>
        /// A test for SetToEnd
        /// </summary>
        [Test]
        public virtual void TestSetToEnd()
        {
            InsertDefaultEntryByIndex(0);
            ITimeSeriesEntryCursor cursor = CreateCursor();

            while (true)
            {
                if (!cursor.MoveNext())
                    break;
            }

            Assert.IsNull(cursor.Current);
            Assert.IsTrue(cursor.MovePrevious());
            ITimeSeriesEntry entry = cursor.Current;

            cursor.SetToEnd();
            Assert.IsTrue(cursor.MovePrevious());
            Assert.IsTrue(TimeSeriesComparisons.CompareTimeSeriesEntry(entry, cursor.Current));
        }

        // *****************************************************************************************
        /// <summary>
        /// A test for SetToEnd
        /// </summary>
        [Test]
        public virtual void TestDoubleSetToEnd()
        {
            InsertDefaultEntryByIndex(0);
            ITimeSeriesEntryCursor cursor = CreateCursor();

            cursor.SetToEnd();
            Assert.IsNull(cursor.Current);
            Assert.IsTrue(cursor.MovePrevious());
            ITimeSeriesEntry entry = cursor.Current;

            cursor.SetToEnd();
            Assert.IsTrue(cursor.MovePrevious());
            Assert.IsTrue(TimeSeriesComparisons.CompareTimeSeriesEntry(entry, cursor.Current));
        }


        // *****************************************************************************************
        /// <summary>
        /// A test for SetBefore time stamp
        /// </summary>
        [Test]
        public virtual void TestSetBefore()
        {
            ITimeSeriesEntryCursor cursor = CreateCursor();
            InsertAllDefaultEntries();

            foreach (long timeStamp in DefaultTimeStamps)
            {
                cursor.SetBefore(DateTimeHelper.ToDateTime(timeStamp));
                Assert.IsTrue(cursor.MoveNext());
                Assert.AreEqual(timeStamp, DateTimeHelper.ToLong(cursor.Current.TimeStamp));

                cursor.SetBefore(DateTimeHelper.ToDateTime(timeStamp - 1));
                Assert.IsTrue(cursor.MoveNext());
                Assert.AreEqual(timeStamp, DateTimeHelper.ToLong(cursor.Current.TimeStamp));

                cursor.SetBefore(DateTimeHelper.ToDateTime(timeStamp + 1));
                Assert.AreEqual(timeStamp, DateTimeHelper.ToLong(cursor.Current.TimeStamp));
            }
        }

        // *****************************************************************************************
        /// <summary>
        /// A test for SetBefore time stamp
        /// </summary>
        [Test]
        public virtual void TestSetBeforeLocalTimeStampFails()
        {
            ITimeSeriesEntryCursor cursor = CreateCursor();
            InsertAllDefaultEntries();

            try
            {
                cursor.SetBefore(new DateTime(DefaultTimeStamps[0], DateTimeKind.Local));
                Assert.Fail("SetBefore should not accept DateTime values with and Local DateTimeKind.");
            }
            catch (ArgumentException)
            {
                // good
            }
        }

        // *****************************************************************************************
        /// <summary>
        /// A test for SetBefore time stamp
        /// </summary>
        [Test]
        public virtual void TestSetBeforeUnspecifiedTimeStampFails()
        {
            ITimeSeriesEntryCursor cursor = CreateCursor();
            InsertAllDefaultEntries();

            try
            {
                cursor.SetBefore(new DateTime(DefaultTimeStamps[0], DateTimeKind.Unspecified));
                Assert.Fail("SetBefore should not accept DateTime values with and Unspecified DateTimeKind.");
            }
            catch (ArgumentException)
            {
                // good
            }
        }

        // *****************************************************************************************
        /// <summary>
        /// A test for SetAfter time stamp
        /// </summary>
        [Test]
        public virtual void TestSetAfter()
        {
            ITimeSeriesEntryCursor cursor = CreateCursor();
            InsertAllDefaultEntries();

            foreach (long timeStamp in DefaultTimeStamps)
            {
                cursor.SetAfter(DateTimeHelper.ToDateTime(timeStamp));
                Assert.IsTrue(cursor.MovePrevious());
                Assert.AreEqual(timeStamp, DateTimeHelper.ToLong(cursor.Current.TimeStamp));

                cursor.SetAfter(DateTimeHelper.ToDateTime(timeStamp + 1));
                Assert.IsTrue(cursor.MovePrevious());
                Assert.AreEqual(timeStamp, DateTimeHelper.ToLong(cursor.Current.TimeStamp));

                cursor.SetAfter(DateTimeHelper.ToDateTime(timeStamp - 1));
                Assert.AreEqual(timeStamp, DateTimeHelper.ToLong(cursor.Current.TimeStamp));
            }
        }

        // *****************************************************************************************
        /// <summary>
        /// A test for SetBefore start time
        /// </summary>
        [Test]
        public virtual void TestSetBeforeStartTime()
        {
            ITimeSeriesEntryCursor cursor = CreateCursor();
            InsertAllDefaultEntries();

            cursor.SetBefore(DefaultTimeSeries.TimeInterval.StartTime.AddTicks(-1));
            Assert.IsNull(cursor.Current);
            Assert.IsTrue(cursor.MoveNext());
            Assert.AreEqual(DefaultTimeSeries.TimeInterval.StartTime, cursor.Current.TimeStamp);

            cursor.SetBefore(DateTimeHelper.ToDateTime(DateTimeHelper.ToLong(DefaultTimeSeries.TimeInterval.StartTime) / 2));
            Assert.IsNull(cursor.Current);
            Assert.IsTrue(cursor.MoveNext());
            Assert.AreEqual(DefaultTimeSeries.TimeInterval.StartTime, cursor.Current.TimeStamp);

            cursor.SetBefore(DateTimeHelper.UtcMinValue);
            Assert.IsNull(cursor.Current);
            Assert.IsTrue(cursor.MoveNext());
            Assert.AreEqual(DefaultTimeSeries.TimeInterval.StartTime, cursor.Current.TimeStamp);
        }

        // *****************************************************************************************
        /// <summary>
        /// A test for SetAfter time stamp
        /// </summary>
        [Test]
        public virtual void TestSetAfterEndTime()
        {
            ITimeSeriesEntryCursor cursor = CreateCursor();
            InsertAllDefaultEntries();

            cursor.SetAfter(DefaultTimeSeries.TimeInterval.EndTime.AddTicks(1));
            Assert.IsNull(cursor.Current);
            Assert.IsTrue(cursor.MovePrevious());
            Assert.AreEqual(DefaultTimeSeries.TimeInterval.EndTime, cursor.Current.TimeStamp);

            cursor.SetAfter(DateTimeHelper.ToDateTime(DateTimeHelper.ToLong(DefaultTimeSeries.TimeInterval.StartTime) * 2));
            Assert.IsNull(cursor.Current);
            Assert.IsTrue(cursor.MovePrevious());
            Assert.AreEqual(DefaultTimeSeries.TimeInterval.EndTime, cursor.Current.TimeStamp);

            cursor.SetAfter(DateTimeHelper.UtcMaxValue);
            Assert.IsNull(cursor.Current);
            Assert.IsTrue(cursor.MovePrevious());
            Assert.AreEqual(DefaultTimeSeries.TimeInterval.EndTime, cursor.Current.TimeStamp);
        }

        // *****************************************************************************************
        /// <summary>
        /// A test for SetBefore time stamp
        /// </summary>
        [Test]
        public virtual void TestSetAfterLocalTimeStampFails()
        {
            ITimeSeriesEntryCursor cursor = CreateCursor();
            InsertAllDefaultEntries();

            try
            {
                cursor.SetAfter(new DateTime(DefaultTimeStamps[0], DateTimeKind.Local));
                Assert.Fail("SetAfter should not accept DateTime values with and Local DateTimeKind.");
            }
            catch (ArgumentException)
            {
                // good
            }
        }

        // *****************************************************************************************
        /// <summary>
        /// A test for SetBefore time stamp
        /// </summary>
        [Test]
        public virtual void TestSetAfterUnspecifiedTimeStampFails()
        {
            ITimeSeriesEntryCursor cursor = CreateCursor();
            InsertAllDefaultEntries();

            try
            {
                cursor.SetAfter(new DateTime(DefaultTimeStamps[0], DateTimeKind.Unspecified));
                Assert.Fail("SetAfter should not accept DateTime values with and Unspecified DateTimeKind.");
            }
            catch (ArgumentException)
            {
                // good
            }
        }

        // *****************************************************************************************
        /// <summary>
        /// A test for SetBefore from time stamps after the end
        /// </summary>
        [Test]
        public virtual void TestSetBeforeFromAfterEnd()
        {
            ITimeSeriesEntryCursor cursor = CreateCursor();
            InsertAllDefaultEntries();

            cursor.SetBefore(DefaultTimeSeries.TimeInterval.EndTime.AddTicks(1));
            Assert.IsNotNull(cursor.Current);
            Assert.AreEqual(DefaultTimeSeries.TimeInterval.EndTime, cursor.Current.TimeStamp);

            cursor.SetBefore(DateTimeHelper.UtcMaxValue);
            Assert.IsNotNull(cursor.Current);
            Assert.AreEqual(DefaultTimeSeries.TimeInterval.EndTime, cursor.Current.TimeStamp);
        }

        // *****************************************************************************************
        /// <summary>
        /// A test for SetBefore from time stamps before the end
        /// </summary>
        [Test]
        public virtual void TestSetBeforeFromBeforeStart()
        {
            ITimeSeriesEntryCursor cursor = CreateCursor();
            InsertAllDefaultEntries();

            cursor.SetBefore(DefaultTimeSeries.TimeInterval.StartTime.AddTicks(-1));
            Assert.IsNull(cursor.Current);
            Assert.IsTrue(cursor.MoveNext());
            Assert.AreEqual(DefaultTimeSeries.TimeInterval.StartTime, cursor.Current.TimeStamp);

            cursor.SetBefore(DateTimeHelper.UtcMinValue);
            Assert.IsNull(cursor.Current);
            Assert.IsTrue(cursor.MoveNext());
            Assert.AreEqual(DefaultTimeSeries.TimeInterval.StartTime, cursor.Current.TimeStamp);
        }

        // *****************************************************************************************
        /// <summary>
        /// A test for SetAfter from time stamps after the end
        /// </summary>
        [Test]
        public virtual void TestSetAfterFromAfterEnd()
        {
            ITimeSeriesEntryCursor cursor = CreateCursor();
            InsertAllDefaultEntries();

            cursor.SetAfter(DefaultTimeSeries.TimeInterval.EndTime.AddTicks(1));
            Assert.IsNull(cursor.Current);
            Assert.IsTrue(cursor.MovePrevious());
            Assert.AreEqual(DefaultTimeSeries.TimeInterval.EndTime, cursor.Current.TimeStamp);

            cursor.SetAfter(DateTimeHelper.UtcMaxValue);
            Assert.IsNull(cursor.Current);
            Assert.IsTrue(cursor.MovePrevious());
            Assert.AreEqual(DefaultTimeSeries.TimeInterval.EndTime, cursor.Current.TimeStamp);
        }

        // *****************************************************************************************
        /// <summary>
        /// A test for SetAfter from time stamps before the start
        /// </summary>
        [Test]
        public virtual void TestSetAfterFromBeforeStart()
        {
            ITimeSeriesEntryCursor cursor = CreateCursor();
            InsertAllDefaultEntries();

            cursor.SetAfter(DefaultTimeSeries.TimeInterval.StartTime.AddTicks(-1));
            Assert.IsNotNull(cursor.Current);
            Assert.AreEqual(DefaultTimeSeries.TimeInterval.StartTime, cursor.Current.TimeStamp);

            cursor.SetAfter(DateTimeHelper.UtcMinValue);
            Assert.IsNotNull(cursor.Current);
            Assert.AreEqual(DefaultTimeSeries.TimeInterval.StartTime, cursor.Current.TimeStamp);
        }



        // *****************************************************************************************
        /// <summary>
        /// A test for IEnumerator.Current
        /// </summary>
        [Test]
        public virtual void TestCurrentForIEnumerator()
        {
            ITimeSeriesEntryCursor cursor = CreateCursor();
            InsertAllDefaultEntries();
            // get an IEnumerator over a time series
            IEnumerator enumerator = cursor;

            // check that it can move and retrieve an entry
            Assert.IsTrue(enumerator.MoveNext());
            ITimeSeriesEntry timeSeriesEntry1 = (ITimeSeriesEntry)enumerator.Current;
            Assert.IsNotNull(timeSeriesEntry1);

            // check that the IEnumerator is a correct Cursor
            ITimeSeriesEntryCursor timeSeriesEntryCursor = enumerator as ITimeSeriesEntryCursor;
            Assert.IsNotNull(timeSeriesEntryCursor);
            Assert.IsNotNull(timeSeriesEntryCursor.Current);

            // check that the corresponding cursor gets the same entry
            ITimeSeriesEntry timeSeriesEntry2 = timeSeriesEntryCursor.Current;
            Assert.IsTrue(TimeSeriesComparisons.CompareTimeSeriesEntry(timeSeriesEntry1, timeSeriesEntry2));

            // and that it is the same entry as retrieving it from a native cursor
            cursor.SetToStart();
            cursor.MoveNext();
            ITimeSeriesEntry timeSeriesEntry3 = cursor.Current;
            Assert.IsTrue(TimeSeriesComparisons.CompareTimeSeriesEntry(timeSeriesEntry2, timeSeriesEntry3));
        }


        // *****************************************************************************************
        /// <summary>
        /// A test for Current at invalid position
        /// </summary>
        [Test]
        public virtual void TestCurrentBeforeStartOrBehindEnd()
        {
            ITimeSeriesEntryCursor cursor = CreateCursor();
            InsertAllDefaultEntries();

            cursor.SetToStart();
            Assert.IsNull(cursor.Current);

            ITimeSeriesEntry timeSeriesEntry = cursor.Current;
            Assert.IsNull(timeSeriesEntry);


            cursor.SetToEnd();
            Assert.IsNull(cursor.Current);

            timeSeriesEntry = cursor.Current;
            Assert.IsNull(timeSeriesEntry);
        }

        // *****************************************************************************************
        /// <summary>
        /// A test for Seek time stamp
        /// </summary>
        [Test]
        public virtual void TestSeekTimeStamp()
        {
            ITimeSeriesEntryCursor cursor = CreateCursor();
            InsertAllDefaultEntries();

            // seek time stamp shall return the entry with the correct time stamp
            foreach (long timeStamp in DefaultTimeStamps)
            {
                cursor.Seek(DateTimeHelper.ToDateTime(timeStamp));
                Assert.AreEqual(timeStamp, DateTimeHelper.ToLong(cursor.Current.TimeStamp));
            }

            // seek time stamp shall return the entry with the next smaller time stamp
            foreach (long timeStamp in DefaultTimeStamps)
            {
                cursor.Seek(DateTimeHelper.ToDateTime(timeStamp + 1));
                Assert.AreEqual(timeStamp, DateTimeHelper.ToLong(cursor.Current.TimeStamp));
            }
        }


        // *****************************************************************************************
        /// <summary>
        /// A test for Seek time stamp before the Start
        /// </summary>
        [Test]
        public virtual void TestSeekTimeStampBeforeStart()
        {
            ITimeSeriesEntryCursor cursor = CreateCursor();
            InsertAllDefaultEntries();

            Assert.IsTrue(cursor.MoveNext());
            Assert.IsNotNull(cursor.Current);

            // get the first timestamp
            DateTime timeStamp = cursor.Current.TimeStamp;

            // try to seek before the start
            Assert.IsFalse(cursor.Seek(timeStamp - new TimeSpan(100)));
            Assert.IsNull(cursor.Current);
        }


        // *****************************************************************************************
        /// <summary>
        /// A test for Seek time stamp behind the End
        /// </summary>
        [Test]
        public virtual void TestSeekTimeStampBehindEnd()
        {
            ITimeSeriesEntryCursor cursor = CreateCursor();
            InsertAllDefaultEntries();

            cursor.SetToEnd();
            Assert.IsNull(cursor.Current);
            Assert.IsTrue(cursor.MovePrevious());
            Assert.IsNotNull(cursor.Current);

            // remember the entry and get its timestamp
            ITimeSeriesEntry timeSeriesEntry = cursor.Current;
            DateTime timeStamp = timeSeriesEntry.TimeStamp;

            // try to seek behind the end; will result in pointing to the last entry (see documentation of Seek(TimeStamp))
            Assert.IsTrue(cursor.Seek(timeStamp + new TimeSpan(100)));
            Assert.IsNotNull(cursor.Current);

            // check that we are indeed at the last entry
            Assert.IsTrue(TimeSeriesComparisons.CompareTimeSeriesEntry(timeSeriesEntry, cursor.Current));
        }


        // *****************************************************************************************
        /// <summary>
        /// Try to give a dateTime with DateTimeKind.Local. This should go wrong
        /// </summary>
        [Test]
        public virtual void TestSeekTimeStampWrongKind()
        {
            ITimeSeriesEntryCursor cursor = CreateCursor();
            try
            {
                DateTime dateTime = new DateTime(0, DateTimeKind.Local);

                cursor.Seek(dateTime);
                Assert.Fail("Seeking with a date time with local DateTimeKind must fail");
            }
            catch (ArgumentException)
            {
                // ok
            }
            try
            {
                DateTime dateTime = new DateTime(0, DateTimeKind.Unspecified);

                cursor.Seek(dateTime);
                Assert.Fail("Seeking with a date time with unspecified DateTimeKind must fail");
            }
            catch (ArgumentException)
            {
                // ok
            }
        }

        // *****************************************************************************************
        /// <summary>
        /// Try to give a dateTime with DateTimeKing.Local. This should go wrong
        /// </summary>
        [Test]
        public virtual void TestSetBeforeTimeStampWrongKind()
        {
            ITimeSeriesEntryCursor cursor = CreateCursor();
            try
            {
                DateTime dateTime = new DateTime(0, DateTimeKind.Local);

                cursor.SetBefore(dateTime);
                Assert.Fail("Seeking with a date time with local DateTimeKind must fail");
            }
            catch (ArgumentException)
            {
                // ok
            }
            try
            {
                DateTime dateTime = new DateTime(0, DateTimeKind.Unspecified);

                cursor.SetBefore(dateTime);
                Assert.Fail("Seeking with a date time with unspecified DateTimeKind must fail");
            }
            catch (ArgumentException)
            {
                // ok
            }
        }


        // *****************************************************************************************
        /// <summary>
        /// Try to give a dateTime with DateTimeKing.Local. This should go wrong
        /// </summary>
        [Test]
        public virtual void TestSetAfterTimeStampWrongKind()
        {
            ITimeSeriesEntryCursor cursor = CreateCursor();
            try
            {
                DateTime dateTime = new DateTime(0, DateTimeKind.Local);

                cursor.SetAfter(dateTime);
                Assert.Fail("Seeking with a date time with local DateTimeKind must fail");
            }
            catch (ArgumentException)
            {
                // ok
            }
            try
            {
                DateTime dateTime = new DateTime(0, DateTimeKind.Unspecified);

                cursor.SetAfter(dateTime);
                Assert.Fail("Seeking with a date time with unspecified DateTimeKind must fail");
            }
            catch (ArgumentException)
            {
                // ok
            }
        }


        // *****************************************************************************************
        /// <summary>
        /// A test for Seek offset for special border values
        /// </summary>
        [Test]
        public void TestSeekTimeSpanSpecialValueAtEnd()
        {
            ITimeSeriesEntryCursor cursor = CreateCursor();
            InsertAllDefaultEntries();

            // show that cursor works as expected for a time series with "normal" values
            cursor.Seek(TimeSpan.FromTicks(-1), SeekPosition.END); // go to second last element
            Assert.IsTrue(cursor.MoveNext()); // go to last element
            Assert.IsNotNull(cursor.Current);
            Assert.IsFalse(cursor.MoveNext());

            InsertDefaultEntryByTimeStamp(MaximumTimeStamp);

            // show that cursor still works
            cursor.Seek(TimeSpan.FromTicks(-1), SeekPosition.END); // go to second last element
            Assert.IsTrue(cursor.MoveNext()); // go to last element
            Assert.IsNotNull(cursor.Current);
            Assert.IsFalse(cursor.MoveNext());
        }

       

        // *****************************************************************************************
        /// <summary>
        /// A test for cursor behaviour before the beginning
        /// </summary>
        [Test]
        public virtual void TestWalkingMilesBeforeBegin()
        {
            ITimeSeriesEntryCursor cursor = CreateCursor();
            InsertDefaultEntryByIndex(0);

            cursor.SetToStart();
            Assert.IsNull(cursor.Current);

            // you cannot reach a valid entry before the beginning
            for (int i = 1; i < 20; ++i)
            {
                Assert.IsFalse(cursor.MovePrevious());
            }

            // one step must be enough to get to the first entry
            Assert.IsTrue(cursor.MoveNext());
            Assert.IsNotNull(cursor.Current);
        }


        // *****************************************************************************************
        /// <summary>
        /// A test for cursor behaviour before the beginning
        /// </summary>
        [Test]
        public virtual void TestSeekingMilesBeforeBegin()
        {
            ITimeSeriesEntryCursor cursor = CreateCursor();
            InsertAllDefaultEntries();

            TimeSpan fullDistance = DefaultTimeSeries.TimeInterval.EndTime - 
                                    DefaultTimeSeries.TimeInterval.StartTime;

            // go into the middle of the timeseries
            cursor.Seek(DefaultTimeSeries.TimeInterval.StartTime + new TimeSpan(fullDistance.Ticks / 2));
            Assert.IsNotNull(cursor.Current);

            // you cannot reach a valid entry far before the beginning
            cursor.Seek(-fullDistance, SeekPosition.CURRENT);
            Assert.IsNull(cursor.Current);

            // one step must be enough to get to the first entry
            Assert.IsTrue(cursor.MoveNext());
            Assert.IsNotNull(cursor.Current);
        }


        // *****************************************************************************************
        /// <summary>
        /// A test for cursor behaviour after the end
        /// </summary>
        [Test]
        public virtual void TestWalkingMilesAfterEnd()
        {
            ITimeSeriesEntryCursor cursor = CreateCursor();
            InsertAllDefaultEntries();

            cursor.SetToEnd();
            Assert.IsNull(cursor.Current);

            // you cannot reach a valid entry behind the end
            for (int i = 1; i < 20; ++i)
            {
                Assert.IsFalse(cursor.MoveNext());
            }

            // one step must be enough to get to the last entry
            Assert.IsTrue(cursor.MovePrevious());
            Assert.IsNotNull(cursor.Current);
        }


        // *****************************************************************************************
        /// <summary>
        /// A test for cursor behaviour after the end
        /// </summary>
        [Test]
        public virtual void TestSeekingMilesAfterEnd()
        {
            ITimeSeriesEntryCursor cursor = CreateCursor();
            InsertAllDefaultEntries();

            TimeSpan fullDistance = DefaultTimeSeries.TimeInterval.EndTime - 
                                    DefaultTimeSeries.TimeInterval.StartTime;

            // go into the middle of the timeseries
            cursor.Seek(DefaultTimeSeries.TimeInterval.StartTime + new TimeSpan(fullDistance.Ticks / 2));
            Assert.IsNotNull(cursor.Current);

            // seek will always step to the last valid entry
            cursor.Seek(fullDistance, SeekPosition.CURRENT);
            Assert.IsNotNull(cursor.Current);
            Assert.IsFalse(cursor.MoveNext());
            Assert.IsNull(cursor.Current);
        }

        // *****************************************************************************************
        /// <summary>
        /// A test for implicit cursor call when using foreach
        /// </summary>
        [Test]
        public virtual void TestCursorWhenUsingForeach()
        {
            InsertAllDefaultEntries();
            ITimeSeries timeSeries = DefaultTimeSeries;

            foreach (ITimeSeriesEntry entry in timeSeries)
            {
                // foreach automatically calls a cursor and then disposes it afterwards
                Assert.IsNotNull(entry.TimeStamp);
            }
        }



        // *****************************************************************************************
        /// <summary>
        /// A test for SetToStart to a UtcMinValue time stamp
        /// </summary>
        [Test]
        public void TestSetToStartAtMinValue()
        {
            InsertDefaultEntryByTimeStamp(MinimumTimeStamp);

            ITimeSeriesEntryCursor cursor = CreateCursor();
            cursor.SetToStart();
            Assert.IsNull(cursor.Current);
            Assert.IsTrue(cursor.MoveNext());
            CheckEntry(cursor.Current);
        }


        // *****************************************************************************************
        /// <summary>
        /// A test actions on empty cursor
        /// </summary>
        [Test]
        public void TestActionsOnEmptyCursor()
        {
            foreach (OperationsHelper.CursorOperation cursorOperation in OperationsHelper.CursorOperations)
            {
                ITimeSeriesEntryCursor cursor = CreateCursor();
                Assert.IsNull(cursor.Current);

                cursorOperation(cursor);
            }
        }

        // *****************************************************************************************
        /// <summary>
        /// A test for SetToEnd to a UtcMaxValue time stamp
        /// </summary>
        [Test]
        public void TestSetToEndAtMaxValue()
        {
            InsertDefaultEntryByTimeStamp(MaximumTimeStamp);

            ITimeSeriesEntryCursor cursor = CreateCursor();
            cursor.SetToEnd();
            Assert.IsNull(cursor.Current);
            Assert.IsTrue(cursor.MovePrevious());
            CheckEntry(cursor.Current);
        }

        // =========================================================================================
        // ** Helper Methods ***********************************************************************
        // =========================================================================================

        // *****************************************************************************************
        /// <summary>
        /// Creates a TimeSeriesEntry at the TimeStamp that is at the given index in 
        /// DefaultTimeStamps.
        /// </summary>
        protected void InsertDefaultEntryByIndex(int index)
        {
            if (index < 0 || index >= DefaultTimeStamps.Count) throw new IndexOutOfRangeException();

            InsertDefaultEntryByTimeStamp(DefaultTimeStamps[index]);
        }

        // *****************************************************************************************
        /// <summary>
        /// Deletes the TimeSeriesEntry at the TimeStamp that is at the given index in 
        /// DefaultTimeStamps.
        /// </summary>
        protected void DeleteDefaultEntryByIndex(int index)
        {
            if (index < 0 || index >= DefaultTimeStamps.Count) throw new IndexOutOfRangeException();

            DeleteDefaultEntryByTimeStamp(DefaultTimeStamps[index]);
        }

        // *****************************************************************************************
        /// <summary>
        /// Inserts an Entry for every TimeStamp in DefaultTimeStamps.
        /// </summary>
        protected void InsertAllDefaultEntries()
        {
            foreach (long defaultTimeStamp in DefaultTimeStamps)
            {
                InsertDefaultEntryByTimeStamp(defaultTimeStamp);
            }
        }

        // *****************************************************************************************
        /// <summary>
        /// Removes all Entries in the DefaultTimeSeries.
        /// </summary>
        protected void RemoveAllEntries()
        {
            DefaultTimeSeries.Clear();
        }

        // *****************************************************************************************
        /// <summary>
        /// Creates a cursor over the DefaultTimeSeries.
        /// </summary>
        protected  abstract ITimeSeriesEntryCursor CreateCursor();
       

        // *****************************************************************************************
        /// <summary>
        /// Return the timeSpan that has to be added to the TimeStamp of the DefaultEntry
        /// at indexA in order to reach the TimeStamp of the DefaultEntry at indexB.
        /// </summary>
        protected TimeSpan TimeSpanBetweenDefaultEntries(int indexA, int indexB)
        {
            if (indexA < 0 || indexA >= DefaultTimeStamps.Count) throw new IndexOutOfRangeException();
            if (indexB < 0 || indexB >= DefaultTimeStamps.Count) throw new IndexOutOfRangeException();

            return TimeSpan.FromTicks(DefaultTimeStamps[indexB] - DefaultTimeStamps[indexA]);
        }

    }
}
