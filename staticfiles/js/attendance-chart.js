/**
 * Attendance Chart JS
 * Handles the rendering and interaction for the attendance chart
 */

document.addEventListener('DOMContentLoaded', function () {
    // Define attendanceData at a scope accessible to all functions
    let attendanceData = {
        labels: [],
        studentPresent: [],
        studentAbsent: [],
        teacherPresent: [],
        teacherAbsent: [],
        startDate: '',
        endDate: '',
        detailApiUrl: ''
    };

    // Function to initialize attendance chart
    function initAttendanceChart(chartData) {
        console.log('Initializing attendance chart with data:', chartData);

        if (!chartData) {
            console.error('No chart data provided');
            return;
        }

        // Store the attendance data
        attendanceData = {
            labels: chartData.labels,
            studentPresent: chartData.studentPresent,
            studentAbsent: chartData.studentAbsent,
            teacherPresent: chartData.teacherPresent,
            teacherAbsent: chartData.teacherAbsent,
            startDate: chartData.startDate,
            endDate: chartData.endDate,
            detailApiUrl: chartData.detailApiUrl
        };

        // Current view state
        let currentView = 'all';

        // Get elements
        const tooltipEl = document.getElementById('tooltip');
        const chartCanvas = document.getElementById('attendanceChart');

        if (!tooltipEl || !chartCanvas) {
            console.error('Required elements not found');
            return;
        }

        const ctx = chartCanvas.getContext('2d');

        // Chart configuration
        const config = {
            type: 'bar',
            data: {
                labels: attendanceData.labels,
                datasets: [
                    {
                        label: 'Students Present',
                        data: attendanceData.studentPresent,
                        backgroundColor: 'rgba(40, 167, 69, 0.7)',
                        borderColor: '#28a745',
                        borderWidth: 2,
                        borderRadius: 4,
                        barPercentage: 0.7,
                        categoryPercentage: 0.8,
                        order: 1
                    },
                    {
                        label: 'Students Absent',
                        data: attendanceData.studentAbsent,
                        backgroundColor: 'rgba(220, 53, 69, 0.7)',
                        borderColor: '#dc3545',
                        borderWidth: 2,
                        borderRadius: 4,
                        barPercentage: 0.7,
                        categoryPercentage: 0.8,
                        order: 2
                    },
                    {
                        label: 'Teachers Present',
                        data: attendanceData.teacherPresent,
                        type: 'line',
                        backgroundColor: 'rgba(0, 123, 255, 0.7)',
                        borderColor: '#007bff',
                        borderWidth: 3,
                        pointBackgroundColor: '#007bff',
                        pointRadius: 5,
                        pointHoverRadius: 7,
                        fill: false,
                        tension: 0.4,
                        order: 0
                    },
                    {
                        label: 'Teachers Absent',
                        data: attendanceData.teacherAbsent,
                        type: 'line',
                        backgroundColor: 'rgba(255, 193, 7, 0.7)',
                        borderColor: '#ffc107',
                        borderWidth: 3,
                        pointBackgroundColor: '#ffc107',
                        pointRadius: 5,
                        pointHoverRadius: 7,
                        fill: false,
                        tension: 0.4,
                        order: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            boxWidth: 10,
                            padding: 20,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        enabled: false,
                        external: function (context) {
                            const { chart, tooltip } = context;

                            if (tooltip.opacity === 0) {
                                tooltipEl.style.display = 'none';
                                return;
                            }

                            if (tooltip.body) {
                                const title = tooltip.title[0];
                                const dataPoints = tooltip.body.map(b => b.lines[0]);

                                // Create tooltip content
                                let tooltipContent = `<div style="font-weight: bold; margin-bottom: 6px;">${title}</div>`;

                                // Add each data point with appropriate color
                                if (dataPoints.length > 0 && !attendanceChart.data.datasets[0].hidden) {
                                    tooltipContent += `<div style="color: #28a745; margin-bottom: 4px;"><span style="display:inline-block;width:10px;height:10px;background:#28a745;margin-right:5px;border-radius:50%;"></span>${dataPoints[0]}</div>`;
                                }
                                if (dataPoints.length > 1 && !attendanceChart.data.datasets[1].hidden) {
                                    tooltipContent += `<div style="color: #dc3545; margin-bottom: 4px;"><span style="display:inline-block;width:10px;height:10px;background:#dc3545;margin-right:5px;border-radius:50%;"></span>${dataPoints[1]}</div>`;
                                }
                                if (dataPoints.length > 2 && !attendanceChart.data.datasets[2].hidden) {
                                    tooltipContent += `<div style="color: #007bff; margin-bottom: 4px;"><span style="display:inline-block;width:10px;height:10px;background:#007bff;margin-right:5px;border-radius:50%;"></span>${dataPoints[2]}</div>`;
                                }
                                if (dataPoints.length > 3 && !attendanceChart.data.datasets[3].hidden) {
                                    tooltipContent += `<div style="color: #ffc107; margin-bottom: 4px;"><span style="display:inline-block;width:10px;height:10px;background:#ffc107;margin-right:5px;border-radius:50%;"></span>${dataPoints[3]}</div>`;
                                }

                                tooltipEl.innerHTML = tooltipContent;

                                // Position tooltip
                                const { offsetLeft: positionX, offsetTop: positionY } = chart.canvas;

                                tooltipEl.style.display = 'block';
                                tooltipEl.style.left = positionX + tooltip.caretX + 'px';
                                tooltipEl.style.top = positionY + tooltip.caretY - 120 + 'px';
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Dates',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        },
                        ticks: {
                            font: {
                                size: 12
                            }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        title: {
                            display: true,
                            text: 'Number of Attendees',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        },
                        ticks: {
                            precision: 0,
                            font: {
                                size: 12
                            }
                        }
                    }
                }
            }
        };

        // Initialize chart
        let attendanceChart = new Chart(ctx, config);
        console.log('Chart initialized');

        // Function to update visible datasets based on the current view
        function updateVisibleDatasets() {
            switch (currentView) {
                case 'students':
                    attendanceChart.data.datasets[0].hidden = false; // Student Present
                    attendanceChart.data.datasets[1].hidden = false; // Student Absent
                    attendanceChart.data.datasets[2].hidden = true;  // Teacher Present
                    attendanceChart.data.datasets[3].hidden = true;  // Teacher Absent
                    break;
                case 'teachers':
                    attendanceChart.data.datasets[0].hidden = true;  // Student Present
                    attendanceChart.data.datasets[1].hidden = true;  // Student Absent
                    attendanceChart.data.datasets[2].hidden = false; // Teacher Present
                    attendanceChart.data.datasets[3].hidden = false; // Teacher Absent
                    break;
                case 'present':
                    attendanceChart.data.datasets[0].hidden = false; // Student Present
                    attendanceChart.data.datasets[1].hidden = true;  // Student Absent
                    attendanceChart.data.datasets[2].hidden = false; // Teacher Present
                    attendanceChart.data.datasets[3].hidden = true;  // Teacher Absent
                    break;
                case 'absent':
                    attendanceChart.data.datasets[0].hidden = true;  // Student Present
                    attendanceChart.data.datasets[1].hidden = false; // Student Absent
                    attendanceChart.data.datasets[2].hidden = true;  // Teacher Present
                    attendanceChart.data.datasets[3].hidden = false; // Teacher Absent
                    break;
                case 'all':
                default:
                    attendanceChart.data.datasets[0].hidden = false; // Student Present
                    attendanceChart.data.datasets[1].hidden = false; // Student Absent
                    attendanceChart.data.datasets[2].hidden = false; // Teacher Present
                    attendanceChart.data.datasets[3].hidden = false; // Teacher Absent
                    break;
            }

            attendanceChart.update();
            console.log('Chart view updated to:', currentView);
        }

        // Function to fetch new attendance data for a specific date range
        async function fetchAttendanceData(startDate, endDate) {
            try {
                // Show loading state
                const updateButton = document.getElementById('updateDateRange');
                if (!updateButton) {
                    console.error('Update button not found');
                    return false;
                }

                updateButton.disabled = true;
                updateButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';

                console.log(`Fetching attendance data from ${startDate} to ${endDate}`);

                const response = await fetch(`/api/attendance/?start_date=${startDate}&end_date=${endDate}`);

                if (!response.ok) {
                    const errorText = await response.text();
                    console.error(`API error (${response.status}): ${errorText}`);
                    throw new Error(`Failed to fetch attendance data: ${response.statusText}`);
                }

                const data = await response.json();
                console.log('Received data:', data);

                // Validate data from API
                if (!data.labels || !data.student_present || !data.student_absent ||
                    !data.teacher_present || !data.teacher_absent) {
                    throw new Error('Required attendance data is missing in API response');
                }

                // Update attendance data
                attendanceData = {
                    labels: data.labels,
                    studentPresent: data.student_present,
                    studentAbsent: data.student_absent,
                    teacherPresent: data.teacher_present,
                    teacherAbsent: data.teacher_absent,
                    startDate: data.start_date,
                    endDate: data.end_date,
                    detailApiUrl: data.detail_api_url
                };

                // Update chart data
                attendanceChart.data.labels = attendanceData.labels;
                attendanceChart.data.datasets[0].data = attendanceData.studentPresent;
                attendanceChart.data.datasets[1].data = attendanceData.studentAbsent;
                attendanceChart.data.datasets[2].data = attendanceData.teacherPresent;
                attendanceChart.data.datasets[3].data = attendanceData.teacherAbsent;

                // Update view based on current selection
                updateVisibleDatasets();

                // Reset button state
                updateButton.disabled = false;
                updateButton.textContent = 'Apply';

                console.log('Chart updated with new data');
                return true;
            } catch (error) {
                console.error('Error fetching attendance data:', error);

                const updateButton = document.getElementById('updateDateRange');
                if (updateButton) {
                    updateButton.disabled = false;
                    updateButton.textContent = 'Apply';
                }

                alert(`Failed to fetch attendance data: ${error.message}`);
                return false;
            }
        }

        // Set initial values for date inputs
        const startDateInput = document.getElementById('startDate');
        const endDateInput = document.getElementById('endDate');

        if (startDateInput && attendanceData.startDate) {
            startDateInput.value = attendanceData.startDate;
        }

        if (endDateInput && attendanceData.endDate) {
            endDateInput.value = attendanceData.endDate;
        }

        // Add event listeners

        // View selector
        const viewSelector = document.getElementById('chartViewSelector');
        if (viewSelector) {
            viewSelector.addEventListener('change', function (e) {
                currentView = e.target.value;
                console.log('View changed to:', currentView);
                updateVisibleDatasets();
            });
        }

        // Date range update
        const updateButton = document.getElementById('updateDateRange');
        if (updateButton) {
            updateButton.addEventListener('click', function (e) {
                e.preventDefault();

                const startDate = startDateInput.value;
                const endDate = endDateInput.value;

                console.log('Date range button clicked:', startDate, 'to', endDate);

                if (!startDate || !endDate) {
                    alert('Please select both start and end dates.');
                    return;
                }

                if (new Date(endDate) < new Date(startDate)) {
                    alert('End date must be after start date.');
                    return;
                }

                fetchAttendanceData(startDate, endDate);
            });
        }

        // Print PDF functionality
        const printButton = document.getElementById('printAttendanceChart');
        if (printButton) {
            printButton.addEventListener('click', function () {
                console.log('Print button clicked');
                generateAttendancePDF();
            });
        }
    }

    // Make the function globally available
    window.initAttendanceChart = initAttendanceChart;

    // Function to generate PDF attendance report
    window.generateAttendancePDF = async function () {
        // Use a global flag to prevent multiple simultaneous generations
        if (window.pdfGenerationInProgress === true) {
            console.log('PDF generation already in progress');
            return;
        }

        // Set the flag to indicate generation is in progress
        window.pdfGenerationInProgress = true;

        try {
            // Check if jsPDF is available
            if (typeof window.jspdf === 'undefined') {
                console.error('jsPDF library not loaded. Cannot generate PDF.');
                alert('PDF generation failed: Required libraries not loaded.');
                window.pdfGenerationInProgress = false;
                return;
            }

            // Show loading indicator
            const printButton = document.getElementById('printAttendanceChart');
            const originalButtonText = printButton.innerHTML;
            printButton.disabled = true;
            printButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating...';

            // Get detailed attendance data for the selected date range
            const startDate = attendanceData.startDate;
            const endDate = attendanceData.endDate;
            const detailApiUrl = '/attendance/api/attendance/detail/';

            // Fetch detailed attendance records with names and statuses
            console.log(`Fetching detailed attendance data from ${startDate} to ${endDate}`);
            const response = await fetch(`${detailApiUrl}?start_date=${startDate}&end_date=${endDate}`);

            if (!response.ok) {
                throw new Error(`Failed to fetch attendance details: ${response.statusText}`);
            }

            const detailData = await response.json();
            console.log('Received detailed attendance data:', detailData);

            // Create new jsPDF instance
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();

            // Title and header
            doc.setFontSize(18);
            doc.setFont('helvetica', 'bold');
            doc.text('Attendance Report', 105, 20, { align: 'center' });

            // Date range
            doc.setFontSize(12);
            doc.setFont('helvetica', 'normal');
            const dateRange = `Date Range: ${startDate} to ${endDate}`;
            doc.text(dateRange, 105, 30, { align: 'center' });

            let currentY = 40;

            // Add student attendance section if student data exists
            if (detailData.students && detailData.students.length > 0) {
                // Student attendance section
                doc.setFontSize(14);
                doc.setFont('helvetica', 'bold');
                doc.text('Student Attendance', 20, currentY);
                currentY += 10;

                // Create student attendance table
                const studentHeaders = ['Date', 'Name', 'Status', 'Remarks'];
                const studentRows = [];

                detailData.students.forEach(record => {
                    studentRows.push([
                        record.date,
                        `${record.student_first_name} ${record.student_last_name}`,
                        record.status.charAt(0).toUpperCase() + record.status.slice(1), // Capitalize status
                        record.remarks || ''
                    ]);
                });

                // Generate student attendance table
                doc.autoTable({
                    head: [studentHeaders],
                    body: studentRows,
                    startY: currentY,
                    headStyles: {
                        fillColor: [56, 142, 60], // Green for students
                        textColor: 255,
                        fontStyle: 'bold',
                        halign: 'center'
                    },
                    alternateRowStyles: {
                        fillColor: [240, 248, 240]
                    },
                    styles: {
                        fontSize: 9,
                        cellPadding: 3
                    }
                });

                currentY = doc.lastAutoTable.finalY + 15;
            }

            // Add teacher attendance section if teacher data exists
            if (detailData.teachers && detailData.teachers.length > 0) {
                // Teacher attendance section
                doc.setFontSize(14);
                doc.setFont('helvetica', 'bold');
                doc.text('Teacher Attendance', 20, currentY);
                currentY += 10;

                // Create teacher attendance table
                const teacherHeaders = ['Date', 'Name', 'Status', 'Remarks'];
                const teacherRows = [];

                detailData.teachers.forEach(record => {
                    teacherRows.push([
                        record.date,
                        `${record.teacher_first_name} ${record.teacher_last_name}`,
                        record.status.charAt(0).toUpperCase() + record.status.slice(1), // Capitalize status
                        record.remarks || ''
                    ]);
                });

                // Generate teacher attendance table
                doc.autoTable({
                    head: [teacherHeaders],
                    body: teacherRows,
                    startY: currentY,
                    headStyles: {
                        fillColor: [41, 98, 255], // Blue for teachers
                        textColor: 255,
                        fontStyle: 'bold',
                        halign: 'center'
                    },
                    alternateRowStyles: {
                        fillColor: [240, 240, 250]
                    },
                    styles: {
                        fontSize: 9,
                        cellPadding: 3
                    }
                });

                currentY = doc.lastAutoTable.finalY + 15;
            }

            // Add summary statistics
            doc.setFontSize(14);
            doc.setFont('helvetica', 'bold');
            doc.text('Summary Statistics', 20, currentY);
            currentY += 10;

            // Calculate statistics
            let studentPresentCount = 0;
            let studentAbsentCount = 0;
            let teacherPresentCount = 0;
            let teacherAbsentCount = 0;

            if (detailData.students) {
                detailData.students.forEach(record => {
                    if (record.status === 'present') {
                        studentPresentCount++;
                    } else if (record.status === 'absent') {
                        studentAbsentCount++;
                    }
                });
            }

            if (detailData.teachers) {
                detailData.teachers.forEach(record => {
                    if (record.status === 'present') {
                        teacherPresentCount++;
                    } else if (record.status === 'absent') {
                        teacherAbsentCount++;
                    }
                });
            }

            const totalStudents = studentPresentCount + studentAbsentCount;
            const totalTeachers = teacherPresentCount + teacherAbsentCount;

            const studentAttendanceRate = totalStudents > 0 ?
                ((studentPresentCount / totalStudents) * 100).toFixed(1) + '%' : 'N/A';

            const teacherAttendanceRate = totalTeachers > 0 ?
                ((teacherPresentCount / totalTeachers) * 100).toFixed(1) + '%' : 'N/A';

            // Add summary table
            const summaryHeaders = ['Category', 'Present', 'Absent', 'Attendance Rate'];
            const summaryRows = [
                ['Students', studentPresentCount, studentAbsentCount, studentAttendanceRate],
                ['Teachers', teacherPresentCount, teacherAbsentCount, teacherAttendanceRate]
            ];

            doc.autoTable({
                head: [summaryHeaders],
                body: summaryRows,
                startY: currentY,
                headStyles: {
                    fillColor: [66, 66, 66],
                    textColor: 255,
                    fontStyle: 'bold',
                    halign: 'center'
                },
                styles: {
                    fontSize: 10,
                    cellPadding: 5
                }
            });

            // Add footer
            const finalY = doc.lastAutoTable.finalY + 15;
            doc.setFontSize(10);
            doc.setFont('helvetica', 'italic');
            doc.text(`Generated on: ${new Date().toLocaleString()}`, 105, finalY, { align: 'center' });

            // Save the PDF
            doc.save(`Attendance_Report_${startDate}_to_${endDate}.pdf`);
            console.log('PDF report with detailed attendance records generated successfully');

            // Reset button state
            printButton.disabled = false;
            printButton.innerHTML = originalButtonText;

            // Reset the flag when done
            window.pdfGenerationInProgress = false;

        } catch (error) {
            console.error('Error generating PDF:', error);

            // Reset button state
            const printButton = document.getElementById('printAttendanceChart');
            if (printButton) {
                printButton.disabled = false;
                printButton.innerHTML = '<i class="fas fa-print"></i> Print';
            }

            // Reset the flag on error
            window.pdfGenerationInProgress = false;
            alert('Failed to generate attendance report: ' + error.message);
        }
    };
}); 