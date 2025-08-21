async function gcaSearchCourse(req, res) {
    const searchCourse = req.body.course_name.trim().toLowerCase();
    try {
        if (!searchCourse) {
            throw new Error("Course name cannot be empty");
        } else {
            const gcaResponse = await fetch(`https://api.golfcourseapi.com/v1/search?search_query=${encodeURIComponent(searchCourse)}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${process.env.GOLFCOURSEAPI_API_KEY}`,
                }
            });
            console.log("GCA Response:", gcaResponse);
            res.gcaResponse.json();
        }
    } catch (error) {
        console.error("Error fetching course data:", error);
        res.status(500).json({ error: "Failed to fetch course data" });
        return;
    }
}

async function gcaGetCourse(req, res) {
    const courseID = req.body.course_id;
    const gcaResponse = await fetch(`https://api.golfcourseapi.com/v1/courses/${encodeURIComponent(courseID)}`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${process.env.GOLFCOURSEAPI_API_KEY}`,
        }
    });
    res.gcaResponse.json();
}

export { gcaSearchCourse, gcaGetCourse };