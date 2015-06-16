import numpy
import numpy.random
import random
import json
import time
from datetime import datetime
import requests
from scipy.linalg import norm
import time

import os
HOSTNAME = os.environ.get('NEXT_BACKEND_GLOBAL_HOST', 'localhost')+':'+os.environ.get('NEXT_BACKEND_GLOBAL_PORT', '8000')

def run_all(assert_200):
  def timeit(f):
    """ 
    Utility used to time the duration of code execution. This script can be composed with any other script.

    Usage::\n
      def f(n): 
        return n**n  

      def g(n): 
        return n,n**n 

      answer0,dt = timeit(f)(3)
      answer1,answer2,dt = timeit(g)(3)
    """
    def timed(*args, **kw):
      ts = time.time()
      result = f(*args, **kw)
      te = time.time()
      if type(result)==tuple:
        return result + ((te-ts),)
      else:
        return result,(te-ts)
    return timed

  app_id = 'DuelingBanditsPureExploration'
  # assert_200 = False
  num_arms = 10
  true_means = numpy.array(range(num_arms))/float(num_arms)
  total_pulls = num_arms*10
  # total_pulls = 50

  # rm = ResourceManager()

  # print
  # print utils.get_app_about(app_id)
  # print

  # # get all the relevant algs
  # supported_alg_ids = utils.get_app_supported_algs(app_id)
  # print
  # print "supported_alg_ids : " + str(supported_alg_ids)
  # print

  supported_alg_ids = ['BR_LilUCB','BR_Random','BR_SuccElim','BeatTheMean']

  alg_list = []
  for alg_id in supported_alg_ids:
    alg_item = {}
    alg_item['alg_id'] = alg_id
    alg_item['alg_label'] = alg_id
    alg_item['params'] = {}
    alg_list.append(alg_item)

  params = {}
  params['proportions'] = []
  for algorithm in alg_list:
    params['proportions'].append(  { 'alg_label': algorithm['alg_label'] , 'proportion':1./len(alg_list) }  )
  algorithm_management_settings = {}
  algorithm_management_settings['mode'] = 'fixed_proportions'
  algorithm_management_settings['params'] = params


  # input test parameters
  n = num_arms
  delta = 0.01

  participants = []
  for i in range(10):
    participant_uid = '%030x' % random.randrange(16**30)
    participants.append(participant_uid)

  #################################################
  # Test POST Experiment
  #################################################
  initExp_args_dict = {}
  initExp_args_dict['args'] = {}
  initExp_args_dict['args']['n'] = n
  initExp_args_dict['args']['failure_probability'] = delta
  initExp_args_dict['args']['participant_to_algorithm_management'] = 'one_to_many' # 'one_to_one'  #optional field
  initExp_args_dict['args']['algorithm_management_settings'] = algorithm_management_settings #optional field
  initExp_args_dict['args']['alg_list'] = alg_list #optional field
  initExp_args_dict['args']['instructions'] = 'You want instructions, here are your test instructions'
  initExp_args_dict['args']['debrief'] = 'You want a debrief, here is your test debrief'
  initExp_args_dict['args']['context_type'] = 'text'
  initExp_args_dict['args']['context'] = 'Boom baby dueling works'
  initExp_args_dict['app_id'] = app_id
  initExp_args_dict['site_id'] = 'replace this with working site id'
  initExp_args_dict['site_key'] = 'replace this with working site key'


  url = "http://"+HOSTNAME+"/api/experiment"
  response = requests.post(url, json.dumps(initExp_args_dict), headers={'content-type':'application/json'})
  print "POST initExp response =",response.text, response.status_code
  if assert_200: assert response.status_code is 200
  initExp_response_dict = json.loads(response.text)

  exp_uid = initExp_response_dict['exp_uid']
  exp_key = initExp_response_dict['exp_key']

  #################################################
  # Test GET Experiment
  #################################################
  url = "http://"+HOSTNAME+"/api/experiment/"+exp_uid+"/"+exp_key
  response = requests.get(url)
  print "GET experiment response =",response.text, response.status_code
  if assert_200: assert response.status_code is 200
  initExp_response_dict = json.loads(response.text)


  # url = "http://"+HOSTNAME+"/widgets/temp-widget-keys"
  # args_dict={ 'exp_uid':exp_uid,
  #             'exp_key':exp_key,
  #             'n':1, #number of widget keys
  #             'tries':1000,
  #             'duration':10000 }
  # print "temp-widget-keys = " + str(args_dict)
  # response = requests.post(url, json.dumps(args_dict),headers={'content-type':'application/json'})
  # widget_key_dict = json.loads(response.text)
  # widget_keys = widget_key_dict['keys']
  # print "POST temp-widget-keys response = ", response.text, response.status_code


  # url = "http://"+HOSTNAME+"/widgets/getwidget"
  # args_dict={ 'name':'getQuery',
  #             'exp_uid':exp_uid,
  #             'app_id':app_id,
  #             'widget_key':widget_keys[0],
  #             'args':{}}
  # print "getwidget args = " + str(args_dict)
  # response = requests.post(url, json.dumps(args_dict),headers={'content-type':'application/json'})
  # print "POST getwidget response = ", response.text, response.status_code
  # response = requests.get(url)


  for t in range(total_pulls):
    
    # time.sleep(.001)
    print t
    #######################################
    # test POST getQuery #
    #######################################
    getQuery_args_dict = {}
    getQuery_args_dict['exp_uid'] = exp_uid
    getQuery_args_dict['exp_key'] = exp_key
    getQuery_args_dict['args'] = {}
    getQuery_args_dict['args']['participant_uid'] = numpy.random.choice(participants)

    url = 'http://'+HOSTNAME+'/api/experiment/getQuery'
    response,dt = timeit(requests.post)(url, json.dumps(getQuery_args_dict),headers={'content-type':'application/json'})
    print "POST getQuery response = ", response.text, response.status_code
    if assert_200: assert response.status_code is 200
    print "POST getQuery duration = ", dt
    print 
    ts = time.time()

    query_dict = json.loads(response.text)
    query_uid = query_dict['query_uid']
    targets = query_dict['target_indices']
    for target in targets:
      if target['label'] == 'left':
        index_left = target['index']
      if target['label'] == 'right':
        index_right = target['index']
      if target['flag'] == 1:
        index_painted = target['index']

    # generate simulated reward #
    #############################
    reward_left = true_means[index_left] + numpy.random.randn()*0.5
    reward_right = true_means[index_right] + numpy.random.randn()*0.5
    if reward_left>reward_right:
      index_winner = index_left
    else:
      index_winner = index_right

    response_time = time.time() - ts


    #############################################
    # test POST reportAnswer 
    #############################################
    reportAnswer_args_dict = {}
    reportAnswer_args_dict["exp_uid"] = exp_uid
    reportAnswer_args_dict["exp_key"] = exp_key
    reportAnswer_args_dict["args"] = {}
    reportAnswer_args_dict["args"]["query_uid"] = query_uid
    reportAnswer_args_dict["args"]['target_winner'] = index_winner
    reportAnswer_args_dict["args"]['response_time'] = response_time

    url = 'http://'+HOSTNAME+'/api/experiment/reportAnswer'
    print "POST reportAnswer args = ", reportAnswer_args_dict
    response,dt = timeit(requests.post)(url, json.dumps(reportAnswer_args_dict), headers={'content-type':'application/json'})
    print "POST reportAnswer response", response.text, response.status_code
    if assert_200: assert response.status_code is 200
    print "POST reportAnswer duration = ", dt
    print
    reportAnswer_json_response = eval(response.text)


    # # test predict #
    # ################
    # # get stateless app
    # app = utils.get_app(app_id)

    # # convert python dictionary to json dictionary
    # predict_id = 'arm_ranking'
    # params = {'alg_label':alg_label}
    # predict_args_dict = {'predict_id':predict_id,'params':params}
    # predict_args_json = json.dumps(predict_args_dict)

    # print "predict_args_json = " + str(predict_args_json)
    # predict_json,didSucceed,message = app.predict(exp_uid=exp_uid,args_json=predict_args_json)
    # print "predict_response_json = " + str(predict_json)

    # if not didSucceed:
    #   raise Exception(message) 
    # # print "iter %d : pulled arm %d, prediction = %s" % (t,index,predict_json)

    # # convert json dictionary to python dictionary
    # predict_dict = json.loads(predict_json)

  # test getStats #
  ################
  # get stateless app
  # stat_list = rm.get_app_supported_stats(app_id)
  # alg_dict_list = rm.get_algs_for_exp_uid(exp_uid)
  # alg_label_list = [x['alg_label'] for x in alg_dict_list]

  # args_list = []
  # for stat in stat_list:
  #   stat_id = stat['stat_id']
  #   necessary_params = stat['necessary_params']

  #   if ('alg_label' in necessary_params) and ('task' in necessary_params):
  #     for task in ['getQuery','reportAnswer','predict']:
  #       for alg_label in alg_label_list:
  #         getStats_dict = {}
  #         getStats_dict['stat_id'] = stat_id
  #         getStats_dict['params'] = {'alg_label':alg_label,'task':task}
  #         getStats_args_json = json.dumps(getStats_dict)
  #         args_list.append(getStats_args_json)

  #   elif ('alg_label' in necessary_params):
  #     for alg_label in alg_label_list:
  #       getStats_dict = {}
  #       getStats_dict['stat_id'] = stat_id
  #       getStats_dict['params'] = {'alg_label':alg_label}
  #       getStats_args_json = json.dumps(getStats_dict)
  #       args_list.append(getStats_args_json)

  #   elif ('task' in necessary_params):
  #     for task in ['getQuery','reportAnswer','predict']:
  #       getStats_dict = {}
  #       getStats_dict['stat_id'] = stat_id
  #       getStats_dict['params'] = {'task':task}
  #       getStats_args_json = json.dumps(getStats_dict)
  #       args_list.append(getStats_args_json)

  #   else:
  #     getStats_dict = {}
  #     getStats_dict['stat_id'] = stat_id
  #     getStats_dict['params'] = {}
  #     getStats_args_json = json.dumps(getStats_dict)
  #     args_list.append(getStats_args_json)


  # # get stateless app
  # app = utils.get_app(app_id)
  # for getStats_args_json in args_list:
  #   print
  #   print
  #   print "getStats_args_json = " + str(getStats_args_json)
  #   getStats_response_json,didSucceed,message = app.getStats(exp_uid=exp_uid,args_json=getStats_args_json)
  #   # print "getStats_response_json = " 
  #   print getStats_response_json
  #   if not didSucceed:
  #     raise Exception(message) 


  ############################################
  # test POST stats
  ###########################################
  args_list = []

  getStats_args_dict = {}
  getStats_args_dict['stat_id'] = 'most_current_ranking'
  getStats_args_dict['params'] = {'alg_label':'BR_LilUCB'}

  args_list.append(getStats_args_dict)

  getStats_args_dict = {}
  getStats_args_dict["exp_uid"] = exp_uid
  getStats_args_dict["exp_key"] = exp_key

  for args in args_list:
    getStats_args_dict["args"] = args
    url = 'http://'+HOSTNAME+'/api/experiment/stats'
    response = requests.post(url, json.dumps(getStats_args_dict) ,headers={'content-type':'application/json'})
    getStats_json_response = eval(response.text)
    print "/experiment/stats "+args['stat_id'], str(getStats_json_response), response.status_code
    if assert_200: assert response.status_code is 200
    print 


  url = 'http://'+HOSTNAME+'/api/experiment/'+exp_uid+'/'+exp_key+'/participants'
  response = requests.get(url)
  participants_response = eval(response.text)
  print 'participants_response = ' + str(participants_response)

  print "%s : All tests compeleted successfully" % (app_id)

if __name__ == '__main__':
  print HOSTNAME
  run_all(False)
