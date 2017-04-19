#!/usr/bin/python3
#
#
import rospy
import rostopic

from subprocess import Popen, devnull

"""
This function is responsible for implementing a ROS node which periodically
publishes the state of the architecture to the "rec/architecture" topic.

Each message published to this topic describes the topics to which a given node
is currently publishing.
"""
def record_publishers():
    # TODO: why queue_size=10? Surely queue_size=1 is more appropriate?
    pub = rospy.Publisher('rec/architecture_publishers', String, queue_size=10)
    rospy.init_node('architecture_publishers')
    rate = rospy.Rate(10) # 10 Hz (TODO: excessive?)

    previous_state = {}
    while not rospy.is_shutdown():

        # determine the state of the architecture
        # TODO: aren't unpublished topics just as interesting, if not more so?
        topics = rospy.get_published_topics()
       
        # get the current architecture state
        current_state = {}
        for (topic, _) in topics:
            (pubs, subs) = get_publishers_and_subscribers(topic)
            current_state[topic] = {
                'publishers': pubs,
                'subscribers': subs
            }

        # find, and publish, any differences with the previous state
        # TODO
        if last_publish != new_publish:
            p = {}
            for topic in new_publish.keys():
                p[topic] = list(new_publish[topic])
            last_publish = new_publish
            pub.publish(str(p))

        previous_state = current_state
        rate.sleep()

"""
Returns a tuple of sets, containing the names of the subscribers and publishers
to a given topic, respectively.
"""
def publishers_and_subscribers(topic):
    info = rostopic.get_info_text(topic)
    info = [l.strip() for l in info.splitlines()]
    assert info[0].startswith('Type:')
    assert info[2].startswith('Publishers:')
    info = info[3:]

    # find the line where the subscribers list begins
    subscribers_at = info.index('Subscribers:')
    assert subscribers_at != -1

    # get a list of pubs and subs
    get_name = lambda l: l.split(' ')[1]
    publishers = set(get_name(pub) for pub in info[:subscribers_at-1])
    subscribers = set(get_name(sub) for sub in info[subscribers_at:-1])

    return (publishers, subscribers)

if __name__ == "__main__":

    # start recording publishers (in another thread)
    record_publishers()

    # start recording ROS bag
    # TODO: for now, we record ALL topics
    #       in the future, we should record specific topics
    cmd = "rosbag record -a"
    with Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, preexec_fn=preexecute, cwd=sandboxd) as p:

        # TODO: listen out for bad return codes and errors
        try:
            p.communicate(timeout=tlim)

        # TODO: be specific about what sort of exceptions we want to stop
        # recording
        except:
            os.killpg(p.pid, signal.SIGKILL)
